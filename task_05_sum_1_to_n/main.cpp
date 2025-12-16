
#include <iostream>
int main() {
    long long n;
    if (!(std::cin >> n))
        return 0;
    __int128 m = 0;
    long long i = 1;
    for (i = 1; i <= n; ++i) {
        m += i;
    }
    long long out = static_cast<long long>(m);
    std::cout << out << '\n';
    return 0;
}

// #include <iostream>
// int main() {
// long long n;
// if (!(std::cin >> n))
// return 0;
//__int128 m = 0;
// long long i = 1;
// while (i <= n) {
//  m += i;
//++i;
//}
// long long out = static_cast<long long>(acc);
// std::cout << out << '\n';
// return 0;
//}