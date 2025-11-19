
#include <iostream>
int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    unsigned long long n;
    if (!(std::cin >> n)) return 0;
    
    unsigned long long reversed = 0;
    while (n > 0) {
        reversed = reversed * 10 + n % 10;
        n /= 10;
    }
    
    std::cout << reversed << std::endl;
    return 0;
}
