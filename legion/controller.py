from flask import Flask, jsonify

import libs.allTournaments.tournaments as tournaments
import libs.tournament as tournament
import libs.tournamentAnalysis.tournamentAnalysis as tournamentAnalysis

app = Flask(__name__)

@app.route('/api/eloTable')
def get_elo_table():
    data = tournaments.get_all()
    return jsonify(data)

@app.route('/api/tournamentAnalysis')
def get_tournament_analysis(name):
    elo_of_players, groups = tournament.get_elo_of_tournament_players(name)
    cards = tournamentAnalysis.tournament_lists_analysis(name, groups)
    win_rate = tournamentAnalysis.calculate_faction_win_rate(name, groups)
    data = {'Faction Win Rate': win_rate,
            'Deployments': elo_of_players,
            'Conditions': cards}
    return jsonify(data)

if __name__ == '__main__':
    app.run()
