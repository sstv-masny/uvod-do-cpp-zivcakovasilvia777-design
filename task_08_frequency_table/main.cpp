
#include <iostream>
#include <vector>

using namespace std;

int main() {
    int n[101] = {};

    n[1] += 1;
    n[2] += 1;
    n[2] += 1;
    n[100] += 1;
    n[0] += 1;

    for (int hodnota = 0; hodnota < 101; hodnota++) {

        if (n[hodnota] > 0) {
            cout << hodnota << " " << n[hodnota] << "\n";
        }
    }

    return 0;
}