# -*- coding: utf-8 -*-
import streamlit as st
import os
from pathlib import Path

from ui.folder_selector import render_folder_selector
from ui.file_preview import render_file_analysis
from ui.type_selector import render_type_selector, render_process_button
from ui.progress_tracker import render_processing_interface
from functions.file_scanner import scan_directory
from functions.encoding_utils import setup_encoding

# Configurar codificação no início da aplicação
setup_encoding()

def main():
    st.set_page_config(
        page_title="Renomeador de Arquivos",
        page_icon="📁",
        layout="wide"
    )
    
    st.title("📁 Renomeador Inteligente de Arquivos")
    st.markdown("Analise e renomeie seus arquivos com base no conteúdo")
    
    # Inicializar session state
    if 'directory_path' not in st.session_state:
        st.session_state.directory_path = ""
    if 'file_analysis' not in st.session_state:
        st.session_state.file_analysis = None
    if 'selected_types' not in st.session_state:
        st.session_state.selected_types = []
    if 'show_preview' not in st.session_state:
        st.session_state.show_preview = False
    if 'show_history' not in st.session_state:
        st.session_state.show_history = False
    if 'preview_data' not in st.session_state:
        st.session_state.preview_data = None
    
    # Etapa 1: Seleção de Diretório
    st.header("1. Seleção de Diretório")
    directory_path = render_folder_selector()
    
    if directory_path and os.path.exists(directory_path):
        st.session_state.directory_path = directory_path
        
        # Etapa 2: Análise Automática
        st.header("2. Análise do Diretório")
        
        with st.spinner("Analisando arquivos..."):
            file_analysis = scan_directory(directory_path)
            st.session_state.file_analysis = file_analysis
        
        if file_analysis:
            # Etapa 3: Exibição dos Tipos
            st.header("3. Tipos de Arquivo Encontrados")
            render_file_analysis(file_analysis)
            
            # Etapa 4: Seleção de Tipos
            st.header("4. Seleção para Processamento")
            selected_types = render_type_selector(file_analysis)
            st.session_state.selected_types = selected_types
            
            # Etapa 5: Processamento
            if selected_types:
                st.header("5. Processamento")
                render_processing_interface(directory_path, selected_types, file_analysis)

if __name__ == "__main__":
    main()