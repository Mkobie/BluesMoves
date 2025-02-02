import dash
import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, State, dcc

from setup import mixer_btn_names, show_video_dropdown, dance_moves, default_interval
from webapp.move_list import move_list
from webapp.navbar import navbar
from webapp.player_and_mixer import player_and_mixer

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
server = app.server

app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(navbar)
        ]),

        dbc.Row([
            dbc.Col(player_and_mixer, style={"maxHeight": "calc(100vh - 70px)", "overflow": "hidden"}),
            dbc.Col(move_list, width=4),
        ])
    ], fluid=True),

    dcc.Store(id="current-move", data=dance_moves.moves[0].name),
])



def run():
    app.run_server(debug=True)


@callback(
    Output("current-move", "data", allow_duplicate=True),
    Input({'type': 'move-button', 'index': dash.dependencies.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def set_current_move(active_move_button):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    clicked_move_name = eval(triggered_id)['index']
    return clicked_move_name


@callback(
    [
        Output({'type': 'move-button', 'index': dash.dependencies.ALL}, 'color'),
        Output({'type': 'lesson-button', 'index': dash.dependencies.ALL}, 'style'),
    ],
    Input("current-move", "data"),
)
def show_current_move_in_move_list(current_move):
    button_colors = ['primary' if move.name == current_move else 'secondary' for move in dance_moves.moves]
    href_visibility = [{'display': 'block'} if move.name == current_move else {'display': 'none'} for move in dance_moves.moves]

    return button_colors, href_visibility


@callback(
    Output("video-source", "data"),
    Input("current-move", "data"),
    [
        State("mixer-count-interval", "disabled"),
        State("mixer-show-vid", "label"),
    ]
)
def show_current_move_in_video_player(current_move, mixer_disabled, show_mixer_vid):
    if mixer_disabled or (not mixer_disabled and show_mixer_vid == show_video_dropdown[1]):
        return f"assets/{current_move}.mp4"
    else:
        return dash.no_update


@app.callback(
    [
        Output("mixer-button", "children"),
        Output("mixer-button", "color"),
        Output("metronome-button", "disabled"),
        Output({'type': 'move-button', 'index': dash.dependencies.ALL}, 'disabled'),
        Output({'type': 'lesson-button', 'index': dash.dependencies.ALL}, 'disabled'),
    ],
    Input("mixer-button", "n_clicks"),
    State("mixer-button", "children"),
    prevent_initial_call=True
)
def manage_layout_on_mixer_button_press(n_clicks, mixer_button_name):
    if mixer_button_name == mixer_btn_names["start"]:
        # Start the mixer
        mixer_button_name = mixer_btn_names["stop"]
        mixer_button_color = 'primary'
        metronome_button_disabled = False
        move_list_button_enable = [True for move in dance_moves.moves]
    else:
        # Stop the mixer
        mixer_button_name = mixer_btn_names["start"]
        mixer_button_color = 'secondary'
        metronome_button_disabled = False
        move_list_button_enable = [False for move in dance_moves.moves]

    return mixer_button_name, mixer_button_color, metronome_button_disabled, move_list_button_enable, move_list_button_enable


@app.callback(
    [
        Output("metronome-button", "children"),
        Output("metronome-interval", "interval"),
        Output("metronome-interval", "disabled"),

        Output("mixer-count-interval", "disabled"),
        Output("mixer-count-interval", "interval"),
        Output("mixer-sound", "src"),

        Output("current-move", "data", allow_duplicate=True),
    ],
    [
        Input("metronome-button", "n_clicks"),
        Input("metronome-bpm-input", "value"),

        Input("mixer-button", "n_clicks"),
        Input("mixer-count-interval", "n_intervals"),
    ],
    [
        State("metronome-interval", "disabled"),
        State("mixer-button", "children"),
    ],
    prevent_initial_call=True
)
def manage_mixer_and_metronome(metronome_n_clicks, bpm, mixer_n_clicks, n_intervals, metronome_is_disabled, mixer_button_name):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    metronome_button_text = metronome_interval = metronome_disabled = mixer_disabled = mixer_interval = move_file = current_move = dash.no_update

    match triggered_id:
        case "metronome-button":
            if metronome_is_disabled:
                metronome_interval = 60000 / bpm
                metronome_disabled = False
                metronome_button_text = "\U0000266a..."
            else:
                metronome_disabled = True
                metronome_button_text = "\U0000266a"

        case "metronome-bpm-input":
            if not metronome_is_disabled:
                metronome_interval = 60000 / bpm

        case "mixer-button":
            if mixer_button_name == mixer_btn_names["start"]:
                mixer_disabled = False
                mixer_interval = default_interval["ms"]/2
            else:
                mixer_disabled = True

        case "mixer-count-interval":
            new_move = dance_moves.get_move()
            move_file = f"/assets/{new_move.name}.wav"
            mixer_interval = new_move.counts * (60000 / bpm)
            current_move = new_move.name

    return metronome_button_text, metronome_interval, metronome_disabled, mixer_disabled, mixer_interval, move_file, current_move


app.clientside_callback(
    '''
    function(n_intervals) {
        const audioElement = document.querySelector('#mixer-sound');
        if (audioElement) {
            audioElement.currentTime = 0;  // Reset the audio to the beginning
            audioElement.play();  // Play the sound on each interval tick
        }
        return null;
    }
    ''',
    Output('mixer-dummy', 'children'),
    Input('mixer-sound', 'src'),
    prevent_initial_call=True
)


app.clientside_callback(
    """
    function(videoSrc) {
        const videoPlayer = document.getElementById('video-player');
        if (videoPlayer && videoSrc) {
            videoPlayer.src = videoSrc;
            videoPlayer.currentTime = 0;
            videoPlayer.play();
        }
        return null;
    }
    """,
    Output("dummy", "data"),
    Input("video-source", "data")
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


if __name__ == '__main__':
    run()
