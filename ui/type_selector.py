# -*- coding: utf-8 -*-
import streamlit as st
from typing import Dict, List

def render_type_selector(file_analysis: Dict) -> List[str]:
    """
    Renderiza a interface de seleção de tipos de arquivo para processamento
    
    Args:
        file_analysis: Resultado da análise de arquivos
    
    Returns:
        Lista dos tipos selecionados para processamento
    """
    if not file_analysis or not file_analysis['file_types']:
        st.warning("Nenhum tipo de arquivo disponível para seleção.")
        return []
    
    st.subheader("Selecione os tipos de arquivo para processar:")
    
    selected_types = []
    
    # Container para os checkboxes organizados
    with st.container():
        file_types = file_analysis['file_types']
        
        # Organizar em colunas para melhor layout
        if len(file_types) <= 2:
            cols = st.columns(len(file_types))
        else:
            cols = st.columns(3)
        
        col_index = 0
        for file_type, data in file_types.items():
            with cols[col_index % len(cols)]:
                render_type_checkbox(file_type, data, selected_types)
            col_index += 1
    
    # Resumo da seleção
    if selected_types:
        render_selection_summary(file_analysis, selected_types)
    
    return selected_types

def render_type_checkbox(file_type: str, data: Dict, selected_types: List[str]):
    """Renderiza um checkbox para um tipo de arquivo específico"""
    
    icon = data.get('icon', '📄')
    friendly_name = data.get('friendly_name', file_type)
    count = data.get('count', 0)
    extensions = data.get('extensions', [])
    
    # Checkbox customizado com informações visuais
    checkbox_key = f"select_{file_type}"
    
    is_selected = st.checkbox(
        f"{icon} {friendly_name}",
        key=checkbox_key,
        help=f"Processar {count} arquivo(s) do tipo {', '.join(extensions)}"
    )
    
    if is_selected:
        selected_types.append(file_type)
    
    # Informações adicionais abaixo do checkbox
    st.caption(f"{count} arquivo{'s' if count != 1 else ''} • {', '.join(extensions)}")

def render_selection_summary(file_analysis: Dict, selected_types: List[str]):
    """Renderiza o resumo da seleção atual"""
    
    st.divider()
    st.subheader("📋 Resumo da Seleção")
    
    total_files_to_process = 0
    types_info = []
    
    for file_type in selected_types:
        if file_type in file_analysis['file_types']:
            data = file_analysis['file_types'][file_type]
            count = data['count']
            total_files_to_process += count
            types_info.append({
                'icon': data['icon'],
                'name': data['friendly_name'],
                'count': count
            })
    
    # Métricas da seleção
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tipos Selecionados", len(selected_types))
    
    with col2:
        st.metric("Arquivos a Processar", total_files_to_process)
    
    with col3:
        percentage = (total_files_to_process / file_analysis['supported_files'] * 100) if file_analysis['supported_files'] > 0 else 0
        st.metric("% dos Arquivos Suportados", f"{percentage:.1f}%")
    
    # Lista dos tipos selecionados
    if types_info:
        st.write("**Tipos que serão processados:**")
        for info in types_info:
            st.write(f"• {info['icon']} {info['name']}: {info['count']} arquivo{'s' if info['count'] != 1 else ''}")

def render_process_button(selected_types: List[str]) -> bool:
    """
    Renderiza o botão de processamento
    
    Returns:
        True se o botão foi clicado e há tipos selecionados
    """
    if not selected_types:
        st.info("👆 Selecione pelo menos um tipo de arquivo para continuar.")
        return False
    
    st.divider()
    
    # Container centrado para o botão
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        process_clicked = st.button(
            "🚀 Iniciar Processamento",
            type="primary",
            use_container_width=True,
            help=f"Processar {len(selected_types)} tipo(s) de arquivo selecionado(s)"
        )
    
    if process_clicked:
        st.success(f"Iniciando processamento de {len(selected_types)} tipo(s) de arquivo...")
        return True
    
    return False