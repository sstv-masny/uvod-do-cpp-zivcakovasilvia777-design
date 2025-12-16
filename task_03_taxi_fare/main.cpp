
#include <cmath>
#include <iomanip>
#include <iostream>
int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    long long k;
    if (!(std::cin >> k))
        return 0;

    double fare = 4.00;
    if (k > 2) {
        fare += 1.50 * std::ceil(k - 2);
    }

    std::cout << std::fixed << std::setprecision(2) << fare << std::endl;
    return 0;
}
