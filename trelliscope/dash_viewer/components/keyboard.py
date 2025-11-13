"""
Keyboard navigation component for Dash viewer.

Provides keyboard shortcuts for common operations.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


KEYBOARD_SHORTCUTS = {
    'Navigation': [
        {'key': '←/→', 'action': 'Previous/Next page'},
        {'key': 'Home', 'action': 'Go to first page'},
        {'key': 'End', 'action': 'Go to last page'},
    ],
    'Search & Filter': [
        {'key': '/', 'action': 'Focus search input'},
        {'key': 'Esc', 'action': 'Clear search / Close modal'},
    ],
    'View Management': [
        {'key': 'Ctrl+S', 'action': 'Save current view'},
        {'key': 'Ctrl+R', 'action': 'Reset all filters'},
    ],
    'Grid Control': [
        {'key': '+', 'action': 'Increase grid size'},
        {'key': '-', 'action': 'Decrease grid size'},
    ]
}


def create_keyboard_help_modal() -> dbc.Modal:
    """
    Create keyboard shortcuts help modal.

    Returns
    -------
    dbc.Modal
        Modal showing keyboard shortcuts
    """
    # Create shortcut sections
    sections = []
    for category, shortcuts in KEYBOARD_SHORTCUTS.items():
        rows = []
        for shortcut in shortcuts:
            rows.append(
                html.Tr([
                    html.Td(
                        html.Kbd(shortcut['key'], className="bg-secondary text-white px-2 py-1"),
                        style={'width': '30%'}
                    ),
                    html.Td(shortcut['action'])
                ])
            )

        sections.append(
            html.Div([
                html.H6(category, className="mt-3 mb-2"),
                dbc.Table(
                    html.Tbody(rows),
                    bordered=True,
                    size='sm',
                    className="mb-0"
                )
            ])
        )

    return dbc.Modal([
        dbc.ModalHeader(
            dbc.ModalTitle([
                html.I(className="bi bi-keyboard me-2"),
                "Keyboard Shortcuts"
            ])
        ),
        dbc.ModalBody([
            html.P("Use these keyboard shortcuts to navigate more efficiently:"),
            *sections,
            html.Hr(),
            html.P([
                html.I(className="bi bi-info-circle me-2"),
                html.Small("Press ? to toggle this help", className="text-muted")
            ])
        ]),
        dbc.ModalFooter(
            dbc.Button("Close", id="keyboard-help-close", color="secondary")
        )
    ], id="keyboard-help-modal", size="lg", is_open=False)


def create_keyboard_listener() -> html.Div:
    """
    Create keyboard event listener.

    Returns
    -------
    html.Div
        Container with keyboard event listeners
    """
    return html.Div([
        # Keyboard event store
        dcc.Store(id='keyboard-event-store', storage_type='memory'),

        # JavaScript clientside callback for keyboard events
        html.Script("""
            document.addEventListener('keydown', function(e) {
                // Don't capture if typing in an input
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                    // Allow Esc to blur inputs
                    if (e.key === 'Escape') {
                        e.target.blur();
                    }
                    return;
                }

                // Capture keyboard events
                var event_data = {
                    key: e.key,
                    ctrlKey: e.ctrlKey,
                    shiftKey: e.shiftKey,
                    altKey: e.altKey,
                    timestamp: Date.now()
                };

                // Store event (this will trigger Dash callbacks)
                var store = document.getElementById('keyboard-event-store');
                if (store) {
                    store.dispatchEvent(new CustomEvent('input', {
                        detail: event_data
                    }));
                }

                // Prevent default for our shortcuts
                var preventKeys = ['ArrowLeft', 'ArrowRight', 'Home', 'End', '/', '?', '+', '-'];
                if (preventKeys.includes(e.key) || (e.ctrlKey && ['s', 'r'].includes(e.key.toLowerCase()))) {
                    e.preventDefault();
                }
            });
        """)
    ])


def get_keyboard_action(key: str, ctrl: bool = False, shift: bool = False, alt: bool = False) -> str:
    """
    Map keyboard event to action.

    Parameters
    ----------
    key : str
        Key pressed
    ctrl : bool
        Ctrl key held
    shift : bool
        Shift key held
    alt : bool
        Alt key held

    Returns
    -------
    str
        Action name or empty string
    """
    # Navigation
    if key == 'ArrowLeft':
        return 'prev_page'
    elif key == 'ArrowRight':
        return 'next_page'
    elif key == 'Home':
        return 'first_page'
    elif key == 'End':
        return 'last_page'

    # Search
    elif key == '/':
        return 'focus_search'
    elif key == 'Escape':
        return 'clear_search'

    # View management
    elif ctrl and key.lower() == 's':
        return 'save_view'
    elif ctrl and key.lower() == 'r':
        return 'reset_filters'

    # Grid control
    elif key == '+' or key == '=':
        return 'increase_grid'
    elif key == '-' or key == '_':
        return 'decrease_grid'

    # Help
    elif key == '?':
        return 'toggle_help'

    return ''


def create_keyboard_help_button() -> dbc.Button:
    """
    Create button to show keyboard shortcuts.

    Returns
    -------
    dbc.Button
        Button to open keyboard help modal
    """
    return dbc.Button(
        [html.I(className="bi bi-keyboard me-2"), "Shortcuts"],
        id='show-keyboard-help-btn',
        color='link',
        size='sm',
        className="text-muted"
    )
