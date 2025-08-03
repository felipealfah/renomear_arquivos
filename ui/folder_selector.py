# -*- coding: utf-8 -*-
import streamlit as st
import os
from pathlib import Path

def render_folder_selector():
    """Renderiza o componente de seleção de pasta"""
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        directory_path = st.text_input(
            "Caminho do Diretório:",
            value=st.session_state.get('directory_path', ''),
            placeholder="Digite o caminho da pasta ou use o botão para navegar",
            help="Cole o caminho completo da pasta que contém os arquivos a serem renomeados"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Espaçamento para alinhar
        if st.button("📂 Navegar", help="Abrir seletor de pasta"):
            st.info("💡 **Dica**: Cole o caminho da pasta no campo ao lado por enquanto.")
    
    # Validação do diretório
    if directory_path:
        if os.path.exists(directory_path) and os.path.isdir(directory_path):
            st.success(f"✅ Diretório válido: `{directory_path}`")
            
            # Mostrar informações básicas do diretório
            try:
                files = list(Path(directory_path).iterdir())
                total_files = len([f for f in files if f.is_file()])
                total_dirs = len([f for f in files if f.is_dir()])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Arquivos", total_files)
                with col2:
                    st.metric("Subpastas", total_dirs)
                with col3:
                    st.metric("Total de itens", len(files))
                    
                return directory_path
                
            except PermissionError:
                st.error("❌ Sem permissão para acessar este diretório")
                return None
                
        elif directory_path.strip():  # Só mostra erro se não estiver vazio
            st.error("❌ Diretório não encontrado ou inválido")
            return None
    
    return None