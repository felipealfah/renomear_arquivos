# -*- coding: utf-8 -*-
import streamlit as st
from typing import Dict

def render_file_analysis(analysis: Dict):
    """Renderiza a análise dos arquivos encontrados"""
    
    if not analysis or not analysis['file_types']:
        st.warning("Nenhum arquivo suportado encontrado no diretório.")
        return
    
    # Resumo geral
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total de Arquivos", 
            analysis['total_files'],
            help="Todos os arquivos encontrados no diretório"
        )
    
    with col2:
        st.metric(
            "Arquivos Suportados", 
            analysis['supported_files'],
            help="Arquivos que podem ser processados"
        )
    
    with col3:
        st.metric(
            "Tipos Diferentes", 
            len(analysis['file_types']),
            help="Quantos tipos de arquivo diferentes foram encontrados"
        )
    
    st.divider()
    
    # Cards para cada tipo de arquivo
    st.subheader("Arquivos por Tipo")
    
    # Organizar em colunas (máximo 3 por linha)
    file_types = list(analysis['file_types'].items())
    
    for i in range(0, len(file_types), 3):
        cols = st.columns(3)
        
        for j, (file_type, data) in enumerate(file_types[i:i+3]):
            with cols[j]:
                render_file_type_card(file_type, data)
    
    # Detalhes expandíveis
    with st.expander("📋 Ver detalhes dos arquivos"):
        render_file_details(analysis['file_types'])

def render_file_type_card(file_type: str, data: Dict):
    """Renderiza um card para um tipo de arquivo específico"""
    
    icon = data.get('icon', '📄')
    friendly_name = data.get('friendly_name', file_type)
    count = data.get('count', 0)
    extensions = data.get('extensions', [])
    
    # Card container
    with st.container():
        st.markdown(f"""
        <div style="
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin: 5px;
            text-align: center;
            background-color: #000;
        ">
            <h3 style="color:#fff;">{icon}</h3>
            <h4 style="color:#fff;">{friendly_name}</h4>
            <p style="color:#fff;"><strong>{count}</strong> arquivo{'s' if count != 1 else ''}</p>
            <small style="color:#ccc;">{', '.join(extensions)}</small>
        </div>
        """, unsafe_allow_html=True)

def render_file_details(file_types: Dict):
    """Renderiza detalhes expandidos dos arquivos"""
    
    for file_type, data in file_types.items():
        st.subheader(f"{data['icon']} {data['friendly_name']}")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.write(f"**Quantidade:** {data['count']}")
            st.write(f"**Extensões:** {', '.join(data['extensions'])}")
        
        with col2:
            # Lista dos arquivos (limitada para não sobrecarregar a interface)
            files = data['files'][:10]  # Mostrar apenas os primeiros 10
            
            if files:
                st.write("**Arquivos encontrados:**")
                for file_path in files:
                    file_name = file_path.split('/')[-1]  # Apenas o nome do arquivo
                    st.write(f"• {file_name}")
                
                if len(data['files']) > 10:
                    st.write(f"... e mais {len(data['files']) - 10} arquivo(s)")
        
        st.divider()