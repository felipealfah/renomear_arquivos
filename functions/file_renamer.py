# -*- coding: utf-8 -*-
"""
Sistema de renomeação de arquivos com histórico e reversão
Padrão: TituloExtraido_DataHora.extensao
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from .encoding_utils import safe_filename, normalize_text
from .file_readers import get_file_reader

class FileRenamer:
    """Gerenciador de renomeação de arquivos com histórico"""
    
    def __init__(self, base_directory: str):
        self.base_directory = Path(base_directory)
        self.history_file = self.base_directory / ".rename_history.json"
        self.history = self._load_history()
    
    def _load_history(self) -> Dict:
        """Carrega histórico de renomeações"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "operations": [],
            "created_at": datetime.now().isoformat(),
            "last_operation": None
        }
    
    def _save_history(self):
        """Salva histórico de renomeações"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")
    
    def _generate_timestamp(self) -> str:
        """Gera timestamp no formato YYYY-MM-DD_HHhMM"""
        return datetime.now().strftime("%Y-%m-%d_%Hh%M")
    
    def _generate_new_filename(self, title: str, original_path: str, timestamp: str) -> str:
        """
        Gera nome de arquivo seguindo padrão: TituloExtraido_DataHora.extensao
        """
        original_file = Path(original_path)
        extension = original_file.suffix
        
        # Limpar e normalizar título
        clean_title = normalize_text(title) if title else "arquivo"
        clean_title = safe_filename(clean_title, max_length=100)  # Deixar espaço para timestamp
        
        # Remover espaços e caracteres especiais do título
        clean_title = clean_title.replace(' ', '_')
        clean_title = ''.join(c for c in clean_title if c.isalnum() or c in '-_')
        
        # Garantir que não está vazio
        if not clean_title or clean_title == '_':
            clean_title = "arquivo"
        
        # Montar nome final: TituloExtraido_DataHora.extensao
        new_name = f"{clean_title}_{timestamp}{extension}"
        
        return new_name
    
    def _resolve_name_conflict(self, target_path: Path) -> Path:
        """Resolve conflito de nomes adicionando contador"""
        if not target_path.exists():
            return target_path
        
        base_name = target_path.stem
        extension = target_path.suffix
        parent = target_path.parent
        
        counter = 1
        while True:
            new_name = f"{base_name}_{counter:03d}{extension}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1
            
            # Limite de segurança
            if counter > 999:
                # Adicionar timestamp mais preciso
                precise_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:17]
                new_name = f"{base_name}_{precise_timestamp}{extension}"
                return parent / new_name
    
    def preview_rename(self, file_paths: List[str], file_types: List[str]) -> List[Dict]:
        """
        Gera preview da renomeação sem executar
        
        Returns:
            Lista de dicionários com informações de renomeação
        """
        timestamp = self._generate_timestamp()
        preview_results = []
        
        for file_path in file_paths:
            try:
                file_path_obj = Path(file_path)
                
                # Determinar tipo do arquivo
                file_extension = file_path_obj.suffix.lower()
                file_type = self._get_file_type_from_extension(file_extension)
                
                if file_type not in file_types:
                    continue
                
                # Ler conteúdo do arquivo
                reader = get_file_reader(file_type)
                if not reader:
                    preview_results.append({
                        'original_path': file_path,
                        'original_name': file_path_obj.name,
                        'new_name': '',
                        'new_path': '',
                        'status': 'error',
                        'error': f'Leitor não disponível para tipo {file_type}'
                    })
                    continue
                
                read_result = reader.read_file(file_path)
                
                if not read_result['success']:
                    preview_results.append({
                        'original_path': file_path,
                        'original_name': file_path_obj.name,
                        'new_name': '',
                        'new_path': '',
                        'status': 'error',
                        'error': read_result['error']
                    })
                    continue
                
                # Gerar novo nome
                new_filename = self._generate_new_filename(
                    read_result['title'], 
                    file_path, 
                    timestamp
                )
                
                # Resolver conflitos
                target_path = file_path_obj.parent / new_filename
                final_path = self._resolve_name_conflict(target_path)
                
                preview_results.append({
                    'original_path': file_path,
                    'original_name': file_path_obj.name,
                    'new_name': final_path.name,
                    'new_path': str(final_path),
                    'status': 'ready',
                    'title_extracted': read_result['title'],
                    'content_preview': read_result['content_preview'][:100] + '...' if len(read_result.get('content_preview', '')) > 100 else read_result.get('content_preview', ''),
                    'error': ''
                })
                
            except Exception as e:
                preview_results.append({
                    'original_path': file_path,
                    'original_name': Path(file_path).name,
                    'new_name': '',
                    'new_path': '',
                    'status': 'error',
                    'error': str(e)
                })
        
        return preview_results
    
    def execute_rename(self, preview_results: List[Dict]) -> Dict:
        """
        Executa a renomeação baseada no preview
        
        Returns:
            Estatísticas da operação
        """
        operation_id = datetime.now().isoformat()
        successful_renames = []
        failed_renames = []
        
        for item in preview_results:
            if item['status'] != 'ready':
                failed_renames.append({
                    'file': item['original_name'],
                    'error': item['error']
                })
                continue
            
            try:
                original_path = Path(item['original_path'])
                new_path = Path(item['new_path'])
                
                # Verificar se arquivo ainda existe
                if not original_path.exists():
                    failed_renames.append({
                        'file': item['original_name'],
                        'error': 'Arquivo não encontrado'
                    })
                    continue
                
                # Verificar permissões
                if not os.access(original_path.parent, os.W_OK):
                    failed_renames.append({
                        'file': item['original_name'],
                        'error': 'Sem permissão de escrita no diretório'
                    })
                    continue
                
                # Executar renomeação
                original_path.rename(new_path)
                
                successful_renames.append({
                    'original_path': str(original_path),
                    'new_path': str(new_path),
                    'original_name': item['original_name'],
                    'new_name': item['new_name'],
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                failed_renames.append({
                    'file': item['original_name'],
                    'error': str(e)
                })
        
        # Salvar no histórico
        operation_record = {
            'operation_id': operation_id,
            'timestamp': datetime.now().isoformat(),
            'successful_renames': successful_renames,
            'failed_renames': failed_renames,
            'total_files': len(preview_results),
            'successful_count': len(successful_renames),
            'failed_count': len(failed_renames)
        }
        
        self.history['operations'].append(operation_record)
        self.history['last_operation'] = operation_id
        self._save_history()
        
        return {
            'operation_id': operation_id,
            'total_files': len(preview_results),
            'successful': len(successful_renames),
            'failed': len(failed_renames),
            'successful_renames': successful_renames,
            'failed_renames': failed_renames
        }
    
    def revert_operation(self, operation_id: str) -> Dict:
        """Reverte uma operação de renomeação"""
        operation = None
        for op in self.history['operations']:
            if op['operation_id'] == operation_id:
                operation = op
                break
        
        if not operation:
            return {'success': False, 'error': 'Operação não encontrada'}
        
        reverted_count = 0
        failed_reverts = []
        
        for rename_info in operation['successful_renames']:
            try:
                new_path = Path(rename_info['new_path'])
                original_path = Path(rename_info['original_path'])
                
                if new_path.exists():
                    new_path.rename(original_path)
                    reverted_count += 1
                else:
                    failed_reverts.append({
                        'file': rename_info['new_name'],
                        'error': 'Arquivo renomeado não encontrado'
                    })
                    
            except Exception as e:
                failed_reverts.append({
                    'file': rename_info['new_name'],
                    'error': str(e)
                })
        
        return {
            'success': True,
            'reverted_count': reverted_count,
            'failed_reverts': failed_reverts,
            'total_to_revert': len(operation['successful_renames'])
        }
    
    def _get_file_type_from_extension(self, extension: str) -> str:
        """Determina tipo do arquivo pela extensão"""
        extension = extension.lower()
        
        if extension in ['.doc', '.docx']:
            return 'word'
        elif extension in ['.xls', '.xlsx']:
            return 'excel'
        elif extension in ['.ppt', '.pptx']:
            return 'powerpoint'
        elif extension == '.pdf':
            return 'pdf'
        elif extension == '.csv':
            return 'csv'
        else:
            return 'unknown'
    
    def get_history(self) -> Dict:
        """Retorna histórico de operações"""
        return self.history