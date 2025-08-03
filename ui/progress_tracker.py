# -*- coding: utf-8 -*-
"""
Interface de progresso e processamento de arquivos
"""

import streamlit as st
import time
from typing import List, Dict, Any
from functions.file_scanner import get_files_by_type
from functions.file_renamer import FileRenamer

def render_processing_interface(directory_path: str, selected_types: List[str], file_analysis: Dict):
    """
    Renderiza interface completa de processamento com preview e execução
    """
    if not selected_types:
        st.warning("Nenhum tipo de arquivo selecionado.")
        return
    
    # Container para todo o processamento
    processing_container = st.container()
    
    with processing_container:
        # Botão para gerar preview
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔍 Gerar Preview", type="secondary", use_container_width=True):
                st.session_state.show_preview = True
                st.session_state.preview_data = None
        
        with col2:
            if st.button("📜 Ver Histórico", type="secondary", use_container_width=True):
                st.session_state.show_history = True
    
    # Mostrar preview se solicitado
    if st.session_state.get('show_preview', False):
        render_preview_section(directory_path, selected_types, file_analysis)
    
    # Mostrar histórico se solicitado
    if st.session_state.get('show_history', False):
        render_history_section(directory_path)

def render_preview_section(directory_path: str, selected_types: List[str], file_analysis: Dict):
    """Renderiza seção de preview da renomeação"""
    
    st.divider()
    st.subheader("🔍 Preview da Renomeação")
    
    # Obter arquivos dos tipos selecionados
    files_to_process = get_files_by_type(file_analysis, selected_types)
    
    if not files_to_process:
        st.warning("Nenhum arquivo encontrado para os tipos selecionados.")
        return
    
    # Gerar preview
    with st.spinner(f"Analisando {len(files_to_process)} arquivo(s)..."):
        renamer = FileRenamer(directory_path)
        preview_data = renamer.preview_rename(files_to_process, selected_types)
        st.session_state.preview_data = preview_data
    
    # Mostrar estatísticas do preview
    render_preview_stats(preview_data)
    
    # Mostrar tabela de preview
    render_preview_table(preview_data)
    
    # Botões de ação
    render_action_buttons(preview_data, directory_path)

def render_preview_stats(preview_data: List[Dict]):
    """Renderiza estatísticas do preview"""
    
    ready_count = len([p for p in preview_data if p['status'] == 'ready'])
    error_count = len([p for p in preview_data if p['status'] == 'error'])
    total_count = len(preview_data)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Arquivos", total_count)
    
    with col2:
        st.metric("Prontos para Renomear", ready_count, delta=None)
    
    with col3:
        st.metric("Com Erros", error_count, delta=None)
    
    with col4:
        success_rate = (ready_count / total_count * 100) if total_count > 0 else 0
        st.metric("Taxa de Sucesso", f"{success_rate:.1f}%")

def render_preview_table(preview_data: List[Dict]):
    """Renderiza tabela com preview das renomeações"""
    
    st.subheader("📋 Arquivos que serão processados:")
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        show_ready = st.checkbox("✅ Mostrar prontos", value=True)
    
    with col2:
        show_errors = st.checkbox("❌ Mostrar com erros", value=True)
    
    # Filtrar dados
    filtered_data = []
    for item in preview_data:
        if (item['status'] == 'ready' and show_ready) or (item['status'] == 'error' and show_errors):
            filtered_data.append(item)
    
    if not filtered_data:
        st.info("Nenhum arquivo para mostrar com os filtros selecionados.")
        return
    
    # Renderizar cards de preview
    for i, item in enumerate(filtered_data):
        render_preview_card(item, i)

def render_preview_card(item: Dict, index: int):
    """Renderiza um card de preview individual"""
    
    # Definir cor baseada no status
    if item['status'] == 'ready':
        border_color = "#28a745"  # Verde
        status_icon = "✅"
    else:
        border_color = "#dc3545"  # Vermelho
        status_icon = "❌"
    
    with st.container():
        st.markdown(f"""
        <div style="
            border: 2px solid {border_color};
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            background-color: #f8f9fa;
        ">
            <h5 style="color:#000">{status_icon} Arquivo {index + 1}</h5>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.write("**Nome Original:**")
            st.code(item['original_name'])
            
            if item['status'] == 'ready':
                st.write("**Título Extraído:**")
                st.write(f"_{item.get('title_extracted', 'N/A')}_")
        
        with col2:
            if item['status'] == 'ready':
                st.write("**Novo Nome:**")
                st.code(item['new_name'])
                
                if item.get('content_preview'):
                    st.write("**Preview do Conteúdo:**")
                    st.caption(item['content_preview'])
            else:
                st.write("**Erro:**")
                st.error(item['error'])

def render_action_buttons(preview_data: List[Dict], directory_path: str):
    """Renderiza botões de ação para o preview"""
    
    ready_files = [p for p in preview_data if p['status'] == 'ready']
    
    if not ready_files:
        st.warning("Nenhum arquivo pronto para renomeação.")
        return
    
    st.divider()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button(
            f"🚀 Executar Renomeação ({len(ready_files)} arquivo{'s' if len(ready_files) != 1 else ''})",
            type="primary",
            use_container_width=True
        ):
            execute_renaming(preview_data, directory_path)

def execute_renaming(preview_data: List[Dict], directory_path: str):
    """Executa a renomeação com barra de progresso"""
    
    ready_files = [p for p in preview_data if p['status'] == 'ready']
    
    st.subheader("🔄 Executando Renomeação...")
    
    # Barra de progresso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Container para logs em tempo real
    log_container = st.empty()
    logs = []
    
    try:
        # Executar renomeação
        status_text.text("Iniciando processamento...")
        progress_bar.progress(10)
        
        renamer = FileRenamer(directory_path)
        
        status_text.text("Executando renomeações...")
        progress_bar.progress(30)
        
        result = renamer.execute_rename(preview_data)
        
        progress_bar.progress(90)
        status_text.text("Finalizando...")
        
        # Simular um pequeno delay para mostrar progresso
        time.sleep(0.5)
        
        progress_bar.progress(100)
        status_text.text("✅ Processamento concluído!")
        
        # Mostrar resultados
        render_execution_results(result)
        
        # Limpar preview após execução bem-sucedida
        st.session_state.show_preview = False
        st.session_state.preview_data = None
        
    except Exception as e:
        st.error(f"Erro durante a execução: {str(e)}")
        status_text.text("❌ Erro no processamento")

def render_execution_results(result: Dict):
    """Renderiza resultados da execução"""
    
    st.divider()
    st.subheader("📊 Resultados da Renomeação")
    
    # Métricas dos resultados
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Processados", result['total_files'])
    
    with col2:
        st.metric("✅ Sucessos", result['successful'], delta=result['successful'])
    
    with col3:
        st.metric("❌ Falhas", result['failed'], delta=-result['failed'] if result['failed'] > 0 else None)
    
    # Detalhes dos sucessos
    if result['successful_renames']:
        with st.expander(f"✅ Arquivos renomeados com sucesso ({len(result['successful_renames'])})"):
            for rename in result['successful_renames']:
                st.write(f"📄 **{rename['original_name']}** → **{rename['new_name']}**")
    
    # Detalhes das falhas
    if result['failed_renames']:
        with st.expander(f"❌ Arquivos com erro ({len(result['failed_renames'])})"):
            for fail in result['failed_renames']:
                st.write(f"📄 **{fail['file']}**: {fail['error']}")
    
    # Informações sobre reversão
    if result['successful'] > 0:
        st.info(f"💡 **ID da Operação**: `{result['operation_id']}`\n\nGuarde este ID para reverter a operação se necessário.")

def render_history_section(directory_path: str):
    """Renderiza seção de histórico de operações"""
    
    st.divider()
    st.subheader("📜 Histórico de Operações")
    
    renamer = FileRenamer(directory_path)
    history = renamer.get_history()
    
    if not history.get('operations'):
        st.info("Nenhuma operação registrada ainda.")
        return
    
    # Mostrar operações mais recentes primeiro
    operations = sorted(history['operations'], key=lambda x: x['timestamp'], reverse=True)
    
    for i, operation in enumerate(operations[:10]):  # Mostrar últimas 10 operações
        with st.expander(f"Operação {i+1} - {operation['timestamp'][:19]}"):
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total", operation['total_files'])
            
            with col2:
                st.metric("Sucessos", operation['successful_count'])
            
            with col3:
                st.metric("Falhas", operation['failed_count'])
            
            # Botão de reversão
            if operation['successful_count'] > 0:
                if st.button(f"🔄 Reverter Operação", key=f"revert_{operation['operation_id']}"):
                    with st.spinner("Revertendo operação..."):
                        revert_result = renamer.revert_operation(operation['operation_id'])
                        
                        if revert_result['success']:
                            st.success(f"✅ {revert_result['reverted_count']} arquivo(s) revertido(s)")
                            if revert_result['failed_reverts']:
                                st.warning(f"⚠️ {len(revert_result['failed_reverts'])} arquivo(s) não puderam ser revertidos")
                        else:
                            st.error(f"❌ Erro ao reverter: {revert_result['error']}")
                    
                    # Recarregar página para atualizar histórico
                    st.rerun()