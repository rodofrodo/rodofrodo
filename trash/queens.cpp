/*
    2025-11-29
    n-queen problem solution
*/
#include <iostream>
#include <vector>
#include <cstdlib>
#include <limits>
#include <ios>
#include <locale>
#include <string>
using namespace std;

unsigned long long ALL_MASK;
int n, global_print_count = 0;
const int PRINT_LIMIT = 50;

struct space_out_thousands : numpunct<char>
{
    char do_thousands_sep() const { return ' '; }
    string do_grouping() const { return "\3"; }
};

string format_with_spaces(unsigned long long n)
{
    string s = to_string(n);
    int len = s.length();
    for (int i = len - 3; i > 0; i -= 3)
        s.insert(i, " ");
    return s;
}

void print_msg(string msg)
{
    cout.imbue(locale(cout.getloc(), new space_out_thousands));
    cout << msg << endl;
    cout << "Press ENTER to finish the programme...";
    cin.ignore(numeric_limits<streamsize>::max(), '\n');
    cin.get();
}

void print_solution(const vector<int> &pos, bool mirror = false)
{
    if (global_print_count >= PRINT_LIMIT)
        return;
    global_print_count++;
    cout << "Solution no. " << global_print_count << ":\n";
    for (int r = 0; r < n; r++)
    {
        for (int c = 0; c < n; c++)
        {
            int queen_col = mirror ? (n - 1 - pos[r]) : pos[r];
            cout << (queen_col == c ? 'Q' : '.');
        }
        cout << '\n';
    }
    cout << '\n';
}

unsigned long long solve_iterative(unsigned long long init_cols,
                                   unsigned long long init_d1, unsigned long long init_d2,
                                   int start_row, vector<int> *pos_ptr)
{
    static unsigned long long cols_stack[64], d1_stack[64], d2_stack[64], available[64];
    static int col_at_row[64];

    unsigned long long solutions = 0;
    vector<int> &pos = *pos_ptr;

    int row = start_row;
    cols_stack[row] = init_cols;
    d1_stack[row] = init_d1;
    d2_stack[row] = init_d2;
    available[row] = ALL_MASK & ~(init_cols | init_d1 | init_d2);

    while (row >= start_row)
    {
        unsigned long long avail = available[row];
        if (avail)
        {
            unsigned long long bit = avail & -avail;
            available[row] = avail - bit;

            int col = __builtin_ctzll(bit);
            col_at_row[row] = col;
            pos[row] = col;

            cols_stack[row + 1] = cols_stack[row] | bit;
            d1_stack[row + 1] = (d1_stack[row] | bit) << 1;
            d2_stack[row + 1] = (d2_stack[row] | bit) >> 1;
            available[row + 1] = ALL_MASK & ~(cols_stack[row + 1] | d1_stack[row + 1] | d2_stack[row + 1]);

            row++;
            if (row == n)
            {
                solutions++;
                if (global_print_count < PRINT_LIMIT)
                {
                    print_solution(pos, false);
                    if (pos[0] < n - 1 - pos[0])
                    {
                        if (global_print_count < PRINT_LIMIT)
                            print_solution(pos, true);
                    }
                }
                row--;
            }
        }
        else
            row--;
    }
    return solutions;
}

int main()
{
    cout << "Chessboard size (n): ";
    if (!(cin >> n))
        return 0;
    if (n < 1)
    {
        print_msg("Size too small (n must be greater than zero).\n");
        return 0;
    }
    if (n == 1)
    {
        print_msg("Number of solutions: 1\n");
        return 0;
    }
    ALL_MASK = (1ULL << n) - 1ULL;
    int mid = n / 2;
    unsigned long long left_count = 0, middle_count = 0;
    vector<int> pos(n, -1);

    for (int col = 0; col < mid; ++col)
    {
        unsigned long long bit = 1ULL << col;
        pos[0] = col;
        left_count += solve_iterative(bit, bit << 1, bit >> 1, 1, &pos);
    }

    if (n % 2 == 1)
    {
        int col = mid;
        unsigned long long bit = 1ULL << col;
        pos[0] = col;
        middle_count = solve_iterative(bit, bit << 1, bit >> 1, 1, &pos);
    }
    unsigned long long total = left_count * 2ULL + middle_count;
    print_msg("Number of solutions: " + format_with_spaces(total) + "\n");
    return 0;
}
