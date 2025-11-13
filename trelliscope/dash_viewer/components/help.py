"""
Help and documentation components for Dash viewer.

Provides in-app help and feature documentation.
"""

from dash import html
import dash_bootstrap_components as dbc


def create_help_modal() -> dbc.Modal:
    """
    Create help modal with feature documentation.

    Returns
    -------
    dbc.Modal
        Help modal component
    """
    return dbc.Modal([
        dbc.ModalHeader(
            dbc.ModalTitle([
                html.I(className="bi bi-question-circle me-2"),
                "Trelliscope Viewer Help"
            ])
        ),
        dbc.ModalBody([
            # Introduction
            html.Div([
                html.H5("Welcome to Trelliscope", className="mb-3"),
                html.P(
                    "Trelliscope allows you to explore large collections of plots through "
                    "interactive filtering, sorting, and navigation."
                ),
            ], className="mb-4"),

            # Features
            create_help_section(
                "🔍 Search",
                [
                    "Search across all metadata fields",
                    "Results update in real-time",
                    "Use the clear button to reset search"
                ]
            ),

            create_help_section(
                "📐 Layout Controls",
                [
                    "Adjust grid columns and rows (1-10)",
                    "Toggle between row-major and column-major arrangement",
                    "Click 'Apply Layout' to update the grid",
                    "Use 'Reset to Default' to restore original layout"
                ]
            ),

            create_help_section(
                "🏷️ Labels",
                [
                    "Select which metadata appears under panels",
                    "Use 'Select All' or 'Clear All' for quick changes",
                    "Labels update immediately when selections change"
                ]
            ),

            create_help_section(
                "🔽 Filters",
                [
                    "Filter panels by metadata values",
                    "Multiple filters work together (AND logic)",
                    "Clear individual filters or use 'Clear All Filters'"
                ]
            ),

            create_help_section(
                "↕️ Sorting",
                [
                    "Sort panels by any metadata field",
                    "Click column headers to toggle sort direction",
                    "Multiple sorts are supported (first has priority)",
                    "Remove sorts individually or clear all"
                ]
            ),

            create_help_section(
                "👁️ Views",
                [
                    "Save current filter/sort/label state as a named view",
                    "Load saved views from the dropdown",
                    "Delete views you no longer need",
                    "Views persist across sessions"
                ]
            ),

            create_help_section(
                "🖼️ Panel Details",
                [
                    "Click any panel to view full-size version",
                    "Navigate between panels with Previous/Next buttons",
                    "View all metadata for the selected panel",
                    "Press Esc to close the modal"
                ]
            ),

            create_help_section(
                "⌨️ Keyboard Shortcuts",
                [
                    "← / → : Previous/Next page",
                    "/ : Focus search",
                    "Esc : Clear search or close modal",
                    "Press ? to see all shortcuts"
                ]
            ),

            create_help_section(
                "📤 Export",
                [
                    "Export filtered data as CSV",
                    "Save current view configuration as JSON",
                    "Download full display configuration"
                ]
            ),

            # Tips
            html.Hr(),
            html.Div([
                html.H6("💡 Tips", className="mb-2"),
                html.Ul([
                    html.Li("Combine search, filters, and sorts for powerful exploration"),
                    html.Li("Save frequently used filter combinations as views"),
                    html.Li("Use keyboard shortcuts for faster navigation"),
                    html.Li("Hover over panels to see click affordance")
                ])
            ]),

            # Footer
            html.Hr(),
            html.Div([
                html.Small([
                    "For more information, visit the ",
                    html.A(
                        "Trelliscope documentation",
                        href="https://github.com/trelliscope/trelliscope",
                        target="_blank",
                        className="alert-link"
                    ),
                    "."
                ], className="text-muted")
            ])
        ], style={'maxHeight': '70vh', 'overflowY': 'auto'}),
        dbc.ModalFooter([
            dbc.Button(
                [html.I(className="bi bi-keyboard me-2"), "Keyboard Shortcuts"],
                id='help-show-shortcuts-btn',
                color='secondary',
                outline=True,
                size='sm'
            ),
            dbc.Button("Close", id="help-modal-close", color="primary", size='sm')
        ])
    ], id="help-modal", size="lg", is_open=False)


def create_help_section(title: str, items: list) -> html.Div:
    """
    Create a help section.

    Parameters
    ----------
    title : str
        Section title
    items : list
        List of help items

    Returns
    -------
    html.Div
        Help section component
    """
    return html.Div([
        html.H6(title, className="mt-3 mb-2"),
        html.Ul([
            html.Li(item) for item in items
        ], className="small")
    ])


def create_help_button() -> dbc.Button:
    """
    Create help button for navbar.

    Returns
    -------
    dbc.Button
        Help button
    """
    return dbc.Button(
        [html.I(className="bi bi-question-circle me-2"), "Help"],
        id='show-help-btn',
        color='link',
        size='sm',
        className="text-muted"
    )


def create_quick_start_guide() -> dbc.Alert:
    """
    Create quick start guide alert.

    Returns
    -------
    dbc.Alert
        Quick start alert
    """
    return dbc.Alert([
        html.H5([
            html.I(className="bi bi-lightbulb me-2"),
            "Quick Start"
        ], className="alert-heading"),
        html.P([
            "Welcome to Trelliscope! Here's how to get started:"
        ]),
        html.Ol([
            html.Li("Use the search bar to find specific panels"),
            html.Li("Apply filters to narrow down your data"),
            html.Li("Click any panel to view full details"),
            html.Li("Save your favorite filter combinations as views")
        ]),
        html.Hr(),
        html.Div([
            dbc.Button(
                [html.I(className="bi bi-question-circle me-2"), "Learn More"],
                id='quick-start-help-btn',
                color='primary',
                size='sm',
                outline=True,
                className="me-2"
            ),
            dbc.Button(
                "Dismiss",
                id='quick-start-dismiss-btn',
                color='secondary',
                size='sm',
                outline=True
            )
        ])
    ], id='quick-start-alert', color="info", dismissable=True, is_open=False)


def create_feature_tooltip(feature_name: str, description: str) -> dbc.Tooltip:
    """
    Create tooltip for a feature.

    Parameters
    ----------
    feature_name : str
        Name of the feature (used as ID)
    description : str
        Tooltip description

    Returns
    -------
    dbc.Tooltip
        Tooltip component
    """
    return dbc.Tooltip(
        description,
        target=f"{feature_name}-help-icon",
        placement="right"
    )


def create_help_icon(feature_id: str) -> html.I:
    """
    Create help icon for inline help.

    Parameters
    ----------
    feature_id : str
        Feature ID for tooltip targeting

    Returns
    -------
    html.I
        Help icon
    """
    return html.I(
        className="bi bi-question-circle-fill text-muted ms-1",
        id=f"{feature_id}-help-icon",
        style={'cursor': 'help', 'fontSize': '12px'}
    )


# Feature descriptions for tooltips
FEATURE_DESCRIPTIONS = {
    'search': 'Search across all text metadata fields. Results update as you type.',
    'filters': 'Filter panels by metadata values. Multiple filters combine with AND logic.',
    'sorts': 'Sort panels by metadata. Click headers to toggle direction.',
    'views': 'Save and restore filter/sort combinations. Views persist across sessions.',
    'labels': 'Select which metadata fields appear under panels.',
    'layout': 'Adjust the grid size and panel arrangement.',
    'export': 'Export filtered data or view configurations.',
}


def get_feature_description(feature: str) -> str:
    """Get feature description for tooltips."""
    return FEATURE_DESCRIPTIONS.get(feature, '')
