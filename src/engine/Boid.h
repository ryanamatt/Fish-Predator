#ifndef BOID_H
#define BOID_H

#include "Vector2D.h"
#include <vector>
#include <cmath>

class Boid {
public:
    Vector2D pos, vel, accel;
    float maxSpeed = 2.5f;  // Reduced from 4.0f
    float maxForce = 0.15f; // Reduced proportionally from 0.2f
    float worldWidth = 1200.0f;
    float worldHeight = 800.0f;
    float wanderAngle;

    Boid(float x, float y) : pos(x, y), vel(0, 0), accel(0, 0) {
        float angle = ((float)rand() / RAND_MAX) * 6.28318530718f;
        float speed = 1.0f + ((float)rand() / RAND_MAX) * 1.5f; // 1.0-2.5 range
        vel = Vector2D(std::cos(angle) * speed, std::sin(angle) * speed);
        wanderAngle = angle;
    }

    Vector2D wrappedDiff(const Vector2D& a, const Vector2D& b) const {
        float dx = a.x - b.x;
        float dy = a.y - b.y;
        
        if (dx > worldWidth / 2.0f) dx -= worldWidth;
        else if (dx < -worldWidth / 2.0f) dx += worldWidth;
        
        if (dy > worldHeight / 2.0f) dy -= worldHeight;
        else if (dy < -worldHeight / 2.0f) dy += worldHeight;
        
        return Vector2D(dx, dy);
    }

    Vector2D wander() {
        float angleChange = ((float)rand() / RAND_MAX - 0.5f) * 0.5f;
        wanderAngle += angleChange;
        
        float wanderRadius = 2.0f;
        float wanderDistance = 4.0f;
        
        Vector2D circleCenter = vel;
        circleCenter.normalize();
        circleCenter = circleCenter * wanderDistance;
        
        Vector2D displacement(wanderRadius * std::cos(wanderAngle), 
                              wanderRadius * std::sin(wanderAngle));
        
        Vector2D wanderForce = circleCenter + displacement;
        wanderForce.limit(maxForce);
        return wanderForce;
    }

    void flock(const std::vector<Boid*> neighbors, Vector2D predatorPos) {
        Vector2D sepSteer(0, 0), alignSum(0, 0), cohSum(0, 0);
        int sepCount = 0;
        int flockCount = 0;
        
        float alignDistSq = 2500.0f; // 50^2
        float sepDistSq = 625.0f;    // 25^2

        for (Boid* other : neighbors) {
            if (other == this) continue;
            
            Vector2D diff = wrappedDiff(pos, other->pos);
            float dSq = diff.magSq();

            if (dSq < alignDistSq) {
                Vector2D wrappedPos = pos - diff;
                cohSum += wrappedPos;
                alignSum += other->vel;
                flockCount++;

                if (dSq < sepDistSq && dSq > 0.01f) {
                    Vector2D unitDiff = diff;
                    unitDiff.normalize();
                    sepSteer += unitDiff / std::sqrt(dSq);
                    sepCount++;
                }
            }
        }

        if (sepCount > 0) {
            Vector2D steer = sepSteer / (float)sepCount;
            steer.normalize();
            steer = (steer * maxSpeed) - vel;
            steer.limit(maxForce);
            applyForce(steer * 1.5f);
        }
        
        if (flockCount > 0) {
            Vector2D avgVel = alignSum / (float)flockCount;
            Vector2D alignSteer = avgVel - vel;
            alignSteer.limit(maxForce);
            applyForce(alignSteer * 0.3f);

            Vector2D avgPos = cohSum / (float)flockCount;
            applyForce(seek(avgPos) * 0.5f);
        }
        
        applyForce(wander() * 0.8f);
        applyForce(flee(predatorPos) * 3.0f);
    }

    Vector2D seek(Vector2D target) const {
        Vector2D desired = target - pos;
        desired.normalize();
        desired = desired * maxSpeed;
        Vector2D steer = desired - vel;
        steer.limit(maxForce);
        return steer;
    }

    Vector2D flee(Vector2D target) const {
        float panicRadiusSq = 10000.0f;
        Vector2D diff = pos - target;
        float dSq = diff.magSq();
        if (dSq < panicRadiusSq) {
            diff.normalize();
            Vector2D steer = (diff * maxSpeed) - vel;
            steer.limit(maxForce * 2.0f);
            return steer;
        }
        return Vector2D(0, 0);
    }

    void update() {
        vel += accel;
        vel.limit(maxSpeed);
        pos += vel;
        accel = Vector2D(0, 0);
    }

    void applyForce(Vector2D force) { accel += force; }
};

#endif