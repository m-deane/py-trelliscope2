"""
Toast notifications and user feedback components.

Provides visual feedback for user actions and errors.
"""

from dash import html
import dash_bootstrap_components as dbc
from typing import Literal


def create_toast_container() -> html.Div:
    """
    Create container for toast notifications.

    Returns
    -------
    html.Div
        Toast container positioned at top-right
    """
    return html.Div(
        id='toast-container',
        style={
            'position': 'fixed',
            'top': '80px',
            'right': '20px',
            'zIndex': '9999',
            'minWidth': '300px',
            'maxWidth': '400px'
        }
    )


def create_toast(
    message: str,
    title: str = "",
    toast_type: Literal['success', 'info', 'warning', 'danger'] = 'info',
    duration: int = 3000
) -> dbc.Toast:
    """
    Create a toast notification.

    Parameters
    ----------
    message : str
        Toast message
    title : str
        Toast title
    toast_type : str
        Type of toast (success, info, warning, danger)
    duration : int
        Auto-dismiss duration in milliseconds

    Returns
    -------
    dbc.Toast
        Toast notification component
    """
    # Icon based on type
    icons = {
        'success': 'bi-check-circle-fill text-success',
        'info': 'bi-info-circle-fill text-info',
        'warning': 'bi-exclamation-triangle-fill text-warning',
        'danger': 'bi-x-circle-fill text-danger'
    }

    icon_class = icons.get(toast_type, icons['info'])

    return dbc.Toast(
        message,
        header=[
            html.I(className=f"bi {icon_class} me-2"),
            title or toast_type.capitalize()
        ],
        is_open=True,
        dismissable=True,
        duration=duration,
        icon=toast_type,
        style={'minWidth': '300px'}
    )


def create_success_toast(message: str, title: str = "Success") -> dbc.Toast:
    """Create success toast."""
    return create_toast(message, title, 'success')


def create_error_toast(message: str, title: str = "Error") -> dbc.Toast:
    """Create error toast."""
    return create_toast(message, title, 'danger', duration=5000)


def create_warning_toast(message: str, title: str = "Warning") -> dbc.Toast:
    """Create warning toast."""
    return create_toast(message, title, 'warning', duration=4000)


def create_info_toast(message: str, title: str = "Info") -> dbc.Toast:
    """Create info toast."""
    return create_toast(message, title, 'info')


def create_loading_toast(message: str = "Loading...") -> dbc.Toast:
    """Create loading toast (doesn't auto-dismiss)."""
    return dbc.Toast(
        [
            dbc.Spinner(size="sm", className="me-2"),
            message
        ],
        header="Loading",
        is_open=True,
        dismissable=False,
        duration=None,  # Doesn't auto-dismiss
        style={'minWidth': '300px'}
    )


def create_empty_state(
    title: str,
    message: str,
    icon: str = "bi-inbox",
    show_reset: bool = True
) -> html.Div:
    """
    Create empty state component.

    Parameters
    ----------
    title : str
        Empty state title
    message : str
        Empty state message
    icon : str
        Bootstrap icon class
    show_reset : bool
        Show reset filters button

    Returns
    -------
    html.Div
        Empty state component
    """
    children = [
        html.Div([
            html.I(className=f"bi {icon}", style={'fontSize': '48px', 'color': '#6c757d'}),
        ], className="mb-3"),
        html.H5(title, className="text-muted"),
        html.P(message, className="text-muted"),
    ]

    if show_reset:
        children.append(
            dbc.Button(
                [html.I(className="bi bi-arrow-counterclockwise me-2"), "Reset Filters"],
                id='empty-state-reset-btn',
                color='primary',
                outline=True,
                className="mt-3"
            )
        )

    return html.Div(
        children,
        style={
            'textAlign': 'center',
            'padding': '60px 20px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '8px',
            'margin': '40px'
        }
    )


def create_error_boundary(error_message: str) -> html.Div:
    """
    Create error boundary component.

    Parameters
    ----------
    error_message : str
        Error message to display

    Returns
    -------
    html.Div
        Error boundary component
    """
    return html.Div([
        dbc.Alert([
            html.H5([
                html.I(className="bi bi-exclamation-triangle-fill me-2"),
                "Something went wrong"
            ], className="alert-heading"),
            html.P(error_message),
            html.Hr(),
            html.P([
                "Try refreshing the page or ",
                html.A("report this issue", href="#", className="alert-link"),
                "."
            ], className="mb-0 small")
        ], color="danger", className="m-4")
    ])


def create_validation_feedback(
    message: str,
    is_valid: bool = False
) -> html.Div:
    """
    Create validation feedback component.

    Parameters
    ----------
    message : str
        Validation message
    is_valid : bool
        Whether validation passed

    Returns
    -------
    html.Div
        Validation feedback component
    """
    color = "success" if is_valid else "danger"
    icon = "bi-check-circle" if is_valid else "bi-x-circle"

    return html.Div([
        html.I(className=f"bi {icon} me-2"),
        html.Small(message)
    ], className=f"text-{color} mt-1")


# Toast message templates
TOAST_MESSAGES = {
    'view_saved': "View '{name}' saved successfully",
    'view_deleted': "View '{name}' deleted",
    'view_loaded': "View '{name}' loaded",
    'filters_cleared': "All filters cleared",
    'sorts_cleared': "All sorts cleared",
    'search_cleared': "Search cleared",
    'export_success': "Export completed successfully",
    'export_error': "Export failed: {error}",
    'layout_applied': "Layout updated: {ncol}×{nrow}",
    'labels_updated': "{count} labels selected",
    'no_results': "No panels match current filters",
    'network_error': "Network error. Please try again.",
}


def get_toast_message(key: str, **kwargs) -> str:
    """
    Get toast message template.

    Parameters
    ----------
    key : str
        Message key
    **kwargs
        Template variables

    Returns
    -------
    str
        Formatted message
    """
    template = TOAST_MESSAGES.get(key, key)
    try:
        return template.format(**kwargs)
    except KeyError:
        return template
