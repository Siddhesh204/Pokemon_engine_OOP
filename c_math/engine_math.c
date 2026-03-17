// c.math/engine_math.c

// This macro makes sure Windows lets Python read the function
#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

// The raw math function
EXPORT double calculate_damage(int level, int power, int atk_stat, int def_stat, double final_modifier) {
    double base_calc = ((2.0 * level) / 5.0) + 2.0;
    double stat_ratio = (double)atk_stat / (double)def_stat;
    double raw_damage = ((base_calc * power * stat_ratio) / 50.0) + 2.0;
    
    return raw_damage * final_modifier;
}