#ifndef SIMULATION_H
#define SIMULATION_H

#include "Boid.h"
#include "Grid.h"
#include <omp.h>
#include <algorithm>

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

            std::vector<Boid*> neighbors(neighborBuffer, neighborBuffer + found);

            b.flock(neighbors, predatorPos);
            b.update();

            // Boundary wrap
            if (b.pos.x > width) b.pos.x = 0;
            else if (b.pos.x < 0) b.pos.x = width;
            if (b.pos.y > height) b.pos.y = 0;
            else if (b.pos.y < 0) b.pos.y = height;
        }
    }

    void remove_boids(const std::vector<int>& indices) {
        // Sort indices in descending order to remove from back to front
        std::vector<int> sorted_indices = indices;
        std::sort(sorted_indices.begin(), sorted_indices.end(), std::greater<int>());

        for (int idx : sorted_indices) {
            if (idx >= 0 && idx < static_cast<int>(boids.size())) {
                boids.erase(boids.begin() + idx);
            }
        }
    }
};

#endif