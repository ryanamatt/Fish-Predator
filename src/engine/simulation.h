#ifndef SIMULATION_H
#define SIMULATION_H

#include "Boid.h"
#include "Grid.h"
#include <omp.h>

class Simulation {
public:
    std::vector<Boid> boids;
    float width, height;

    Simulation(int count, float w, float h) : width(w), height(h) {
        for(int i=0; i<count; ++i) boids.emplace_back(rand()%int(w), rand()%int(h));
    }

    void step(Vector2D predatorPos) {
        Grid grid(width, height, 50.0f);

        // Grid population (single-threaded is faster due to better cache locality)
        for (auto& b : boids) {
            grid.add(&b);
        }

        int n = static_cast<int>(boids.size());
        
        // Static scheduling: eliminates dynamic scheduling overhead
        // Each thread gets contiguous chunks for better cache performance
        #pragma omp parallel for schedule(static)
        for (int i = 0; i < n; ++i) {
            auto& b = boids[i];
            
            // Reduced buffer - 64 neighbors is plenty for good flocking
            Boid* neighborBuffer[64]; 
            int found = grid.query(b.pos.x, b.pos.y, neighborBuffer, 64);

            b.flock(neighborBuffer, found, predatorPos);
            b.update();

            // Boundary wrap
            if (b.pos.x > width) b.pos.x = 0;
            else if (b.pos.x < 0) b.pos.x = width;
            if (b.pos.y > height) b.pos.y = 0;
            else if (b.pos.y < 0) b.pos.y = height;
        }
    }
};

#endif