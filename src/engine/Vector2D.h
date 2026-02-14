#ifndef VECTOR2D_H
#define VECTOR2D_H

#include <cmath>

struct Vector2D {
    float x, y;

    Vector2D(float x = 0, float y = 0) : x(x), y(y) {}

    Vector2D operator+(const Vector2D& v) const { return Vector2D(x + v.x, y + v.y); }
    Vector2D operator-(const Vector2D& v) const { return Vector2D(x - v.x, y - v.y); }
    Vector2D operator*(float n) const { return Vector2D(x * n, y * n); }
    Vector2D operator/(float n) const { return Vector2D(x / n, y / n); }

    void operator+=(const Vector2D& v) { x += v.x; y += v.y; }

    float magSq() const { return x * x + y * y; }
    float mag() const { return std::sqrt(magSq()); }

    // The "Secret Sauce" for Steering
    void normalize() {
        float m = mag();
        if (m > 0) { x /= m; y /= m; }
    }

    void limit(float max) {
        if (magSq() > max * max) {
            normalize();
            x *= max;
            y *= max;
        }
    }
};

#endif // VECTOR2D_H