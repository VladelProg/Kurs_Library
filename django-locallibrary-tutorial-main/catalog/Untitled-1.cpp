#include <iostream>
#include <thread>
#include <vector>
#include <immintrin.h>
#include <boost/multiprecision/cpp_int.hpp>

using namespace boost::multiprecision;

void partial_sum_simd(long long start, long long end, int128_t& result) {
    int128_t sum = 0;

    __m256i vec_sum = _mm256_setzero_si256();  // Инициализируем вектор для суммирования

    long long i;
    // Обрабатываем блоки по 4 значения с помощью SIMD
    for (i = start; i <= end - 3; i += 4) {
        __m256i vec_i = _mm256_set_epi64x(i + 3, i + 2, i + 1, i);
        vec_sum = _mm256_add_epi64(vec_sum, vec_i);
    }

    // Сохраняем результат из векторного регистра в массив
    long long temp[4];
    _mm256_store_si256((__m256i*)temp, vec_sum);

    // Суммируем значения массива
    for (int j = 0; j < 4; ++j) {
        sum += temp[j];
    }

    // Обрабатываем оставшиеся числа, если их меньше 4
    for (; i <= end; ++i) {
        sum += i;
    }

    result = sum;
}

int main() {
    setlocale(0, "Rus");
    double total = 0;
    for (int i = 1; i <= 10; i++) {
        std::cout << "Запуск теста номер " << i << std::endl;
        auto start = std::chrono::high_resolution_clock::now();
        long long n = 10000000000;
        int num_threads = std::thread::hardware_concurrency();
        //std::cout << ""
        std::vector<std::thread> threads;
        std::vector<int128_t> results(num_threads, 0);

        long long block_size = n / num_threads;

        // Запускаем потоки с векторизацией
        for (int i = 0; i < num_threads; ++i) {
            long long start = i * block_size + 1;
            long long end = (i == num_threads - 1) ? n : (i + 1) * block_size;
            threads.push_back(std::thread(partial_sum_simd, start, end, std::ref(results[i])));
        }

        for (auto& t : threads) {
            t.join();
        }

        // Суммирование результатов
        int128_t total_sum = 0;
        for (const auto& sum : results) {
            total_sum += sum;
        }

        auto end = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> elapsed = end - start;
        total += elapsed.count();
        // Вывод результата
        std::cout << "Сумма от 1 до " << n << " = " << total_sum << std::endl;
        std::cout << "Время обработки программы: " << elapsed.count() << " секунд" << std::endl;
    }
    std::cout << "Среднее время обработки программы: " << total / 10 << " секунд" << std::endl;
    return 0;
}
