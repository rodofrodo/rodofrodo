#include <bits/stdc++.h>
using namespace std;

int n; // rozmar szachownicy
long long solutions = 0; // liczba znalezionych rozwiazan

vector<int> pos; // pozycje hetmanow w kazdym wierszu
int printLimit = 50; // limit rozwiazan do wypisania

/**
 * @brief Rozwiazuje problem n hetmanow za pomoca rekurencyjnego backtrackingu
 * @param row Aktualny wiersz do umieszczenia hetmana
 * @param cols Bitmask reprezentujaca zajete kolumny
 * @param d1 Bitmask reprezentujaca zajete przekatne (lewo-dol)
 * @param d2 Bitmask reprezentujaca zajete przekatne (prawo-dol)
 */
void solve(int row, long long cols, long long d1, long long d2) {
    if (row == n) {
        solutions++;
        if (solutions <= printLimit) {
            cout << "Rozwiazanie " << solutions << ":\n";
            for (int r = 0; r < n; r++) {
                for (int c = 0; c < n; c++)
                    cout << (pos[r] == c ? "Q " : ". ");
                cout << "\n";
            }
            cout << "\n";
        }
        return;
    }

    // Oblicz dostepne pozycje w aktualnym wierszu
    // Dostepne pozycje to te, ktore nie sa atakowane przez inne hetmany
    long long available = ((1LL << n) - 1) & ~(cols | d1 | d2);

    while (available) {
        // Wybierz najmlodszy bit (najmniej znaczacy) z dostepnych pozycji
        long long bit = available & -available;
        available -= bit;

        // liczba zer na końcu liczby binarnej (count trailing zeros).
        // Dzięki temu wiemy, która kolumna odpowiada ustawionemu bitowi.
        int col = __builtin_ctzll(bit);
        pos[row] = col;

        // Rekurencyjnie umiesc hetmana w nastepnym wierszu
        // Aktualizuj bitmaski zajetych kolumn i przekatnych
        solve(row + 1,
              cols | bit,
              (d1 | bit) << 1,
              (d2 | bit) >> 1);
    }
}

/**
 * @brief Funkcja main
 */
int main() {
    cout << "Podaj rozmiar szachownicy (n): ";
    cin >> n;
    pos.resize(n);

    solve(0, 0, 0, 0);

    cout << "Liczba rozwiazan: " << solutions << endl;
}
