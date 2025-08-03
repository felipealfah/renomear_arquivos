# -*- coding: utf-8 -*-
"""
Utilitários para tratamento de codificação de caracteres
Compatível com Windows e diferentes codificações
"""

import os
import sys
import locale
from pathlib import Path
from typing import Optional

def setup_encoding():
    """
    Configura a codificação adequada para o sistema
    """
    # Configurar codificação UTF-8 para stdout/stderr
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
    
    # Configurar locale para português brasileiro se disponível
    try:
        if os.name == 'nt':  # Windows
            locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
        else:  # Linux/Mac
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except locale.Error:
            pass  # Usar locale padrão do sistema

def safe_filename(filename: str, max_length: int = 200) -> str:
    """
    Sanitiza um nome de arquivo para ser seguro em diferentes sistemas
    
    Args:
        filename: Nome do arquivo original
        max_length: Comprimento máximo do nome
    
    Returns:
        Nome de arquivo sanitizado
    """
    # Caracteres proibidos no Windows
    forbidden_chars = '<>:"/\\|?*'
    
    # Substituir caracteres proibidos
    safe_name = filename
    for char in forbidden_chars:
        safe_name = safe_name.replace(char, '_')
    
    # Remover espaços no início/fim
    safe_name = safe_name.strip()
    
    # Substituir múltiplos espaços por um único
    safe_name = ' '.join(safe_name.split())
    
    # Limitar comprimento
    if len(safe_name) > max_length:
        safe_name = safe_name[:max_length].rsplit(' ', 1)[0]
    
    # Garantir que não termine com ponto (problema no Windows)
    safe_name = safe_name.rstrip('.')
    
    # Garantir que não esteja vazio
    if not safe_name:
        safe_name = "arquivo_sem_nome"
    
    return safe_name

def safe_path_join(*paths) -> str:
    """
    Junta caminhos de forma segura, tratando diferentes separadores
    """
    return str(Path(*paths))

def normalize_text(text: str) -> str:
    """
    Normaliza texto removendo caracteres especiais e acentos se necessário
    """
    # Manter acentos mas remover caracteres de controle
    normalized = ''.join(char for char in text if ord(char) >= 32)
    
    # Substituir quebras de linha por espaços
    normalized = normalized.replace('\n', ' ').replace('\r', ' ')
    
    # Remover espaços múltiplos
    normalized = ' '.join(normalized.split())
    
    return normalized

def detect_encoding(file_path: str) -> str:
    """
    Detecta a codificação de um arquivo de texto
    """
    encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read()
            return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    return 'utf-8'  # Fallback

def read_text_file(file_path: str, max_chars: int = 1000) -> Optional[str]:
    """
    Lê arquivo de texto de forma segura, tentando diferentes codificações
    """
    encoding = detect_encoding(file_path)
    
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            content = f.read(max_chars)
        return normalize_text(content)
    except Exception:
        return None