# -*- coding: utf-8 -*-
import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple
from .encoding_utils import safe_path_join

# Mapeamento de extensões para tipos de arquivo
FILE_TYPE_MAPPING = {
    'word': ['.doc', '.docx'],
    'excel': ['.xls', '.xlsx'],
    'powerpoint': ['.ppt', '.pptx'],
    'pdf': ['.pdf'],
    'csv': ['.csv']
}

# Nomes amigáveis para os tipos
FRIENDLY_NAMES = {
    'word': 'Documentos Word',
    'excel': 'Planilhas Excel',
    'powerpoint': 'Apresentações PowerPoint',
    'pdf': 'Documentos PDF',
    'csv': 'Arquivos CSV'
}

# Ícones para cada tipo
TYPE_ICONS = {
    'word': '📄',
    'excel': '📊',
    'powerpoint': '📽️',
    'pdf': '📕',
    'csv': '📈'
}

def get_file_type(file_path: Path) -> str:
    """Determina o tipo de arquivo baseado na extensão"""
    extension = file_path.suffix.lower()
    
    for file_type, extensions in FILE_TYPE_MAPPING.items():
        if extension in extensions:
            return file_type
    
    return 'unknown'

def scan_directory(directory_path: str) -> Dict:
    """
    Escaneia um diretório e categoriza os arquivos por tipo
    
    Returns:
        Dict com informações sobre os arquivos encontrados
    """
    directory = Path(directory_path)
    
    if not directory.exists() or not directory.is_dir():
        return None
    
    # Estrutura para armazenar os resultados
    analysis = {
        'directory': str(directory),
        'file_types': defaultdict(lambda: {
            'count': 0,
            'files': [],
            'extensions': set(),
            'friendly_name': '',
            'icon': ''
        }),
        'total_files': 0,
        'supported_files': 0,
        'unsupported_files': 0
    }
    
    try:
        # Escanear todos os arquivos
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                analysis['total_files'] += 1
                
                file_type = get_file_type(file_path)
                
                if file_type != 'unknown':
                    # Arquivo suportado
                    analysis['supported_files'] += 1
                    analysis['file_types'][file_type]['count'] += 1
                    # Usar representação segura do caminho
                    analysis['file_types'][file_type]['files'].append(safe_path_join(str(file_path)))
                    analysis['file_types'][file_type]['extensions'].add(file_path.suffix.lower())
                    analysis['file_types'][file_type]['friendly_name'] = FRIENDLY_NAMES.get(file_type, file_type)
                    analysis['file_types'][file_type]['icon'] = TYPE_ICONS.get(file_type, '📄')
                else:
                    # Arquivo não suportado
                    analysis['unsupported_files'] += 1
        
        # Converter sets para listas para serialização
        for file_type_data in analysis['file_types'].values():
            file_type_data['extensions'] = list(file_type_data['extensions'])
        
        # Converter defaultdict para dict normal
        analysis['file_types'] = dict(analysis['file_types'])
        
        return analysis
        
    except PermissionError:
        return None

def get_files_by_type(analysis: Dict, file_types: List[str]) -> List[str]:
    """
    Retorna lista de arquivos dos tipos selecionados
    
    Args:
        analysis: Resultado do scan_directory
        file_types: Lista de tipos de arquivo ('word', 'excel', etc.)
    
    Returns:
        Lista de caminhos de arquivo
    """
    files = []
    
    for file_type in file_types:
        if file_type in analysis['file_types']:
            files.extend(analysis['file_types'][file_type]['files'])
    
    return files