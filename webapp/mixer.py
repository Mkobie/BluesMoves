import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output

from setup import bmp_limits, mixer_btn_names, default_interval, show_video_dropdown, \
    metronome_audio, grouping_titles
from webapp.server import app

mixer_settings = dbc.InputGroup(
                            [
                                dbc.InputGroupText("Practice up to"),
                                dbc.DropdownMenu(
                                        label=grouping_titles[0], id="mixer-moves", color="secondary",
                                        children=[dbc.DropdownMenuItem(title, id={'type': 'mixer-moves-dropdown-item', 'index': i}) for i, title in enumerate(grouping_titles)],
                                    ),
                                dbc.InputGroupText("at"),
                                dbc.Input(id="metronome-bpm-input", type="number", value=default_interval["bpm"], min=bmp_limits["min"], max=bmp_limits["max"], step=1, debounce=True),
                                dbc.Button("\U0000266a", id="metronome-button", color="secondary", ),
                                dbc.InputGroupText("bpm"),
                                dbc.DropdownMenu(
                                        label=show_video_dropdown[0], id="mixer-show-vid", color="secondary",
                                        children=[
                                            dbc.DropdownMenuItem(show_video_dropdown[0], id="mixer-show-vid-no"),
                                            dbc.DropdownMenuItem(show_video_dropdown[1], id="mixer-show-vid-yes")
                                        ],
                                    ),
                            ],
                        )

metronome_stuff = html.Div(
    [
        dcc.Interval(id="metronome-interval", interval=600, n_intervals=0, disabled=True),
        html.Div(id="metronome-dummy", style={'display': 'none'}),
        html.Audio(id="metronome-sound", src=metronome_audio, controls=False, style={'display': 'none'})
    ]
)

mixer_stuff = html.Div(
    [
        dcc.Interval(id="mixer-count-interval", interval=0, n_intervals=0, disabled=True),
        html.Div(id="mixer-dummy", style={'display': 'none'}),
        html.Audio(id="mixer-sound", controls=False, style={'display': 'none'}),
    ]
)

mixer = dbc.Row(
                [
                    dbc.Col(
                        [
                            mixer_settings
                        ], width=8
                    ),

                    dbc.Col(
                        [
                            dbc.Button(mixer_btn_names["start"], id="mixer-button", color="secondary"),
                        ]
                    ),

                    metronome_stuff,
                    mixer_stuff

                ], className="mt-3",

            )


app.clientside_callback(
    '''
    function(n_intervals) {
        const audioElement = document.querySelector('#metronome-sound');
        if (audioElement) {
            audioElement.currentTime = 0;  // Reset the audio to the beginning
            audioElement.play();  // Play the sound on each interval tick
        }
        return null;
    }
    ''',
    Output('metronome-dummy', 'children'),
    Input('metronome-interval', 'n_intervals'),
    prevent_initial_call=True
)