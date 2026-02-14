#ifndef GRID_H
#define GRID_H

#include "Boid.h"
#include <vector>
#include <cmath>

class Grid {
    int rows, cols;
    float cellSize;
    float width, height;
    std::vector<std::vector<std::vector<Boid*>>> cells;

public:
    Grid(float w, float h, float cSize) : width(w), height(h), cellSize(cSize) {
        cols = static_cast<int>(std::ceil(width / cellSize));
        rows = static_cast<int>(std::ceil(height / cellSize));
        cells.resize(cols, std::vector<std::vector<Boid*>>(rows));
    }

    void clear() {
        for (int x = 0; x < cols; ++x) {
            for (int y = 0; y < rows; ++y) {
                cells[x][y].clear();
            }
        }
    }

    void add(Boid* b) {
        int ix = static_cast<int>(b->pos.x / cellSize);
        int iy = static_cast<int>(b->pos.y / cellSize);
        
        // Clamp indices to handle boids exactly on the edge
        if (ix < 0) ix = 0; if (ix >= cols) ix = cols - 1;
        if (iy < 0) iy = 0; if (iy >= rows) iy = rows - 1;
        
        cells[ix][iy].push_back(b);
    }

    int query(float px, float py, Boid** buffer, int maxCount) const {
        int ix = static_cast<int>(px / cellSize);
        int iy = static_cast<int>(py / cellSize);
        int count = 0;

        // Query 3x3 grid around the boid with wrapping
        for (int dx = -1; dx <= 1; ++dx) {
            for (int dy = -1; dy <= 1; ++dy) {
                // Use modulo to wrap around edges
                int cx = (ix + dx + cols) % cols;
                int cy = (iy + dy + rows) % rows;
                
                for (Boid* b : cells[cx][cy]) {
                    if (count < maxCount) {
                        buffer[count++] = b;
                    } else {
                        return count;
                    }
                }
            }
        }
        return count;
    }
};

#endif