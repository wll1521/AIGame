import pyxel
import random
import heapq
from collections import deque
import sys

class Game:
    def __init__(self, seed=None):
        # Set the random seed if provided
        if seed is not None:
            random.seed(seed)
            self.seed = seed  # Store the seed
        else:
            self.seed = None

        # Initialize Pyxel window
        pyxel.init(160, 160)
        pyxel.title = "AI Grid Game"

        # Grid dimensions
        self.grid_width = 10
        self.grid_height = 10
        self.tile_size = 16  # Tile size in pixels

        # Player's starting position
        self.player_x = self.grid_width // 2
        self.player_y = self.grid_height // 2

        # Player score starts at 100
        self.score = 100

        # Generate game elements
        self.generate_items()
        self.generate_terrain()

        # Movement costs
        self.movement_costs = {
            'normal': 1,
            'mud': 10,
            'water': 50
        }

        # Visibility map
        self.visible_tiles = set()
        self.update_visibility()

        # Set the default algorithm
        self.algorithm = 'bfs'  # Options: 'astar' or 'bfs'

        # Start Pyxel application
        pyxel.run(self.update, self.draw)

    def generate_items(self):
        self.items = {}
        for _ in range(15):
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) != (self.player_x, self.player_y):
                self.items[(x, y)] = random.choice(['positive'])  #Took out 'negative' in ['positive', 'negative']

    def generate_terrain(self):
        self.terrain = {}
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                terrain_type = random.choices(
                    ['normal', 'mud', 'water'],
                    weights=[0.7, 0.2, 0.1],
                    k=1
                )[0]
                self.terrain[(x, y)] = terrain_type

    def update(self):
        # Check if game is over
        if self.score <= 0:
            if pyxel.btnp(pyxel.KEY_R):
                self.reset_game()
            return  # Skip updates if game is over
        # Update visible tiles
        self.update_visibility()
        # Handle algorithm switching
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.switch_algorithm()
        # Reset game
        if pyxel.btnp(pyxel.KEY_R):
            self.reset_game()
        # AI controls the player
        if pyxel.frame_count % 5 == 0:  # Adjust speed as needed
            self.ai_move()

    
    def reset_game(self):
        # Reset player position
        self.player_x = self.grid_width // 2
        self.player_y = self.grid_height // 2

        # Reset score
        self.score = 100

        # Re-seed the random number generator if seed is provided
        if self.seed is not None:
            random.seed(self.seed)
        else:
            random.seed()  # Use system time or default seed

        # Regenerate items and terrain
        self.generate_items()
        self.generate_terrain()

        # Reset visibility
        self.visible_tiles = set()
        self.update_visibility()

        # Reset algorithm to default if needed
        self.algorithm = 'astar'


    def switch_algorithm(self):
        if self.algorithm == 'astar':
            self.algorithm = 'bfs'
        else:
            self.algorithm = 'astar'

    def move_player(self, dx, dy):
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        if 0 <= new_x < self.grid_width and 0 <= new_y < self.grid_height:
            # Get the terrain of the new tile
            terrain = self.terrain.get((new_x, new_y), 'normal')
            # Get the movement cost
            cost = self.movement_costs.get(terrain, 1)
            # Deduct the cost from the score
            self.score -= cost
            # Check if score is zero or below
            if self.score <= 0:
                self.game_over()
                return
            # Update player's position
            self.player_x = new_x
            self.player_y = new_y
            self.check_for_items()
            self.update_visibility()

    def check_for_items(self):
        if (self.player_x, self.player_y) in self.items:
            item = self.items.pop((self.player_x, self.player_y))
            if item == 'positive':
                self.score += 15
            else:
                self.score -= 200
                # Check for game over after collecting a negative item
                if self.score <= 0:
                    self.game_over()

    def update_visibility(self):
        x, y = self.player_x, self.player_y
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                    self.visible_tiles.add((nx, ny))

    def is_visible(self, position):
        return position in self.visible_tiles

    def draw(self):
        # Clear the screen
        pyxel.cls(0)

        # Draw grid with terrain types
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if (x, y) in self.visible_tiles:
                    terrain = self.terrain.get((x, y), 'normal')
                    color = {
                        'normal': 11,  # Green
                        'mud': 4,     # Brown
                        'water': 12   # Blue
                    }[terrain]
                    pyxel.rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size, color)
                else:
                    # Draw fog
                    pyxel.rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size, 0)

        # Draw items if they are visible
        for (x, y), item in self.items.items():
            if (x, y) in self.visible_tiles:
                color = 11 if item == 'positive' else 8
                pyxel.circ(x * self.tile_size + 8, y * self.tile_size + 8, 4, color)

        # Draw the player if the game is not over
        if self.score > 0:
            pyxel.rect(self.player_x * self.tile_size, self.player_y * self.tile_size, self.tile_size, self.tile_size, 9)

        # Draw the score
        pyxel.text(5, 5, f"Score: {self.score}", 7)
        # Draw the current algorithm
        pyxel.text(5, 15, f"Algorithm: {self.algorithm.upper()}", 7)

        # Display Game Over message if score is zero or below
        if self.score <= 0:
            pyxel.text(50, 80, "Game Over!", pyxel.frame_count % 16)
            pyxel.text(40, 90, "Press 'R' to Restart", 8)

    def game_over(self):
        # Optionally, you can implement additional game over logic here
        pass  # No need to stop Pyxel; just handle game over state

    def ai_move(self):
        if self.score <= 0:
            return  # Do not move if the game is over
        # Find all visible positive items
        positive_items = [pos for pos, item in self.items.items() if item == 'positive' and pos in self.visible_tiles]
        if positive_items:
            # Find the closest visible positive item
            closest_item = min(positive_items, key=lambda pos: self.heuristic((self.player_x, self.player_y), pos))
            # Choose the pathfinding algorithm
            print(f"Using {self.algorithm.upper()} algorithm to find path to {closest_item}")
            if self.algorithm == 'astar':
                path = self.astar((self.player_x, self.player_y), closest_item)
            elif self.algorithm == 'bfs':
                path = self.bfs((self.player_x, self.player_y), closest_item)
            else:
                path = None
            #print path
            if path:
                print(f"Path found: {path}")
            else:
                print("No path found.")
            if path and len(path) > 1:
                next_step = path[1]
                dx = next_step[0] - self.player_x
                dy = next_step[1] - self.player_y
                self.move_player(dx, dy)
        else:
            # No visible positive items, proceed to explore
            self.explore()

    def explore(self):
        if self.score <= 0:
            return  # Do not explore if the game is over
        # Find all unexplored tiles
        all_unexplored = [(x, y) for x in range(self.grid_width) for y in range(self.grid_height) if (x, y) not in self.visible_tiles]
        if not all_unexplored:
            return  # All tiles have been explored

        # Find the closest unexplored tile
        closest_unexplored = min(all_unexplored, key=lambda pos: self.heuristic((self.player_x, self.player_y), pos))

        # Choose the pathfinding algorithm
        if self.algorithm == 'astar':
            path = self.astar_to_unexplored((self.player_x, self.player_y), closest_unexplored)
        elif self.algorithm == 'bfs':
            path = self.bfs_to_unexplored((self.player_x, self.player_y), closest_unexplored)
        else:
            path = None

        if path and len(path) > 1:
            next_step = path[1]
            dx = next_step[0] - self.player_x
            dy = next_step[1] - self.player_y
            self.move_player(dx, dy)
        else:
            # No path found, move randomly
            possible_moves = self.get_neighbors((self.player_x, self.player_y))
            next_step = random.choice(possible_moves)
            dx = next_step[0] - self.player_x
            dy = next_step[1] - self.player_y
            self.move_player(dx, dy)

    def get_neighbors(self, node):
        x, y = node
        neighbors = []
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                neighbors.append((nx, ny))
        return neighbors

    def heuristic(self, a, b):
        # Reduce the heuristic by a factor
        return 0.1 * (abs(a[0] - b[0]) + abs(a[1] - b[1]))

    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def astar(self, start, goal):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == goal:
                return self.reconstruct_path(came_from, current)
            for neighbor in self.get_neighbors(current):
                terrain = self.terrain.get(neighbor, 'normal')
                cost = self.movement_costs.get(terrain, 1)
                tentative_g_score = g_score[current] + cost
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return None  # Path not found

    def astar_to_unexplored(self, start, goal):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == goal:
                return self.reconstruct_path(came_from, current)
            for neighbor in self.get_neighbors(current):
                # Assume unknown terrain is 'normal' for exploration purposes
                terrain = self.terrain.get(neighbor, 'normal')
                cost = self.movement_costs.get(terrain, 1)
                tentative_g_score = g_score[current] + cost
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return None  # Path not found

    def bfs(self, start, goal):
        queue = deque()
        queue.append((start, [start]))
        visited = set()
        visited.add(start)
        while queue:
            current, path = queue.popleft()
            if current == goal:
                return path
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None  # Path not found

    def bfs_to_unexplored(self, start, goal):
        queue = deque()
        queue.append((start, [start]))
        visited = set()
        visited.add(start)
        while queue:
            current, path = queue.popleft()
            if current == goal:
                return path
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None  # Path not found

if __name__ == "__main__":
    seed = None
    if len(sys.argv) > 1:
        seed_arg = sys.argv[1]
        try:
            seed = int(seed_arg)
        except ValueError:
            # Handle non-integer seed values
            seed = hash(seed_arg)
            print(f"Using hashed seed value: {seed}")
    Game(seed)
