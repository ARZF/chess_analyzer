from django.shortcuts import render
from django.http import HttpResponse
import chess
import chess.engine
import chess.pgn
import io


stockfish_path = r'add_your_engine_pass'

def index(request):

    return render(request, 'analyzer/index.html')


def analyze_game(request):
    print("Received request for analyze_game")
    if request.method == 'POST':
        pgn_text = request.POST.get('pgn_text')

        if not pgn_text:
            return HttpResponse("No PGN data provided.")

        try:

            pgn_io = io.StringIO(pgn_text)
            game = chess.pgn.read_game(pgn_io)

            if game is None:
                return HttpResponse("Invalid PGN format. Please check your input.")


            analysis = []
            board = chess.Board()

            try:

                with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
                    for move in game.mainline_moves():
                        board.push(move)


                        result = engine.play(board, chess.engine.Limit(time=0.5))
                        best_move = result.move


                        info = engine.analyse(board, chess.engine.Limit(depth=10))
                        score = info.get("score")


                        if score.is_mate():

                            mate_score = score.relative.moves
                            evaluation = f"Mate in {mate_score}"
                        else:

                            evaluation = f"{score.relative.cp / 100.0:.2f}"


                        analysis.append({
                            'move': move.uci(),
                            'best_move': best_move.uci() if best_move else "End of game",
                            'evaluation': evaluation,
                        })

                context = {
                    'analysis': analysis,
                }
                return render(request, 'analyzer/analysis.html', context)

            except FileNotFoundError:
                return HttpResponse(f"Stockfish engine not found at path: {stockfish_path}")
            except Exception as e:
                return HttpResponse(f"Error analyzing game: {str(e)}")

        except Exception as e:
            return HttpResponse(f"Error parsing PGN: {str(e)}")
    else:
        return HttpResponse("Invalid request method. POST required.")
