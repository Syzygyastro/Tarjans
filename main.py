from manim import *
import networkx as nx
from manim import config

# Set the path to the FFmpeg executable directly in the script
# config.ffmpeg_executable = [ENTER PATH HERE]

class TarjansAlgorithmVisualization(Scene):
    def construct(self):
        # Initialize graph data
        edges = [(1, 2), (2, 3), (3, 1), (3, 4), (4, 5), (5, 6), (6, 4), (7, 6), (7, 8), (8, 7)]
        G = nx.DiGraph()
        G.add_edges_from(edges)
        pos_2d = nx.spring_layout(G, seed=42)  # Layout for node positions with seed for consistency

        # Convert 2D positions to 3D by adding a z-coordinate of 0
        pos = {node: [pos_2d[node][0] * 3, pos_2d[node][1] * 3, 0] for node in G.nodes()}

        # Create nodes with larger dots and labels
        node_radius = 0.2
        nodes = {n: Dot(point=pos[n], radius=node_radius).set_color(BLUE) for n in G.nodes()}
        labels = {n: Text(str(n), font_size=24).next_to(nodes[n], UP) for n in G.nodes()}
        graph_mobjects = VGroup(*nodes.values(), *labels.values())

        # Create edges between nodes
        edges_mobjects = VGroup()
        for u, v in edges:
            edge = Arrow(start=pos[u], end=pos[v], buff=0.1, stroke_width=2, color=WHITE)
            edges_mobjects.add(edge)

        # Display the graph with nodes and edges
        self.play(Create(edges_mobjects), Create(graph_mobjects))
        self.wait(1)

        # Bookkeeping for Tarjan's algorithm
        discovery_time = {node: None for node in G.nodes()}
        low_link = {node: None for node in G.nodes()}
        stack = []
        on_stack = {node: False for node in G.nodes()}
        sccs = []
        time_counter = [0]
        bookkeeping_texts = {}  # To store discovery/low-link text

        # Function to visualize each step and keep track of bookkeeping
        def update_bookkeeping(node, discovery, low_link_value):
            if node in bookkeeping_texts:
                self.play(FadeOut(bookkeeping_texts[node]), run_time=0.5)

            # Display discovery and low-link values beside the graph
            bookkeeping_text = Text(f"{node}: d={discovery}, l={low_link_value}", font_size=24)
            bookkeeping_text.next_to(graph_mobjects, RIGHT, buff=1.5).shift(DOWN * 0.3 * node)
            bookkeeping_texts[node] = bookkeeping_text
            self.play(Write(bookkeeping_text), run_time=0.5)

        # Function to highlight nodes during the traversal
        def highlight_node(node, color):
            self.play(nodes[node].animate.set_color(color), run_time=0.5)

        # Tarjan's Algorithm with visual highlights
        def tarjan(u):
            discovery_time[u] = low_link[u] = time_counter[0]
            time_counter[0] += 1
            stack.append(u)
            on_stack[u] = True

            # Highlight the node as it’s being visited
            highlight_node(u, YELLOW)
            update_bookkeeping(u, discovery_time[u], low_link[u])
            self.wait(0.5)

            for v in G.neighbors(u):
                if discovery_time[v] is None:  # Node v not visited
                    tarjan(v)
                    low_link[u] = min(low_link[u], low_link[v])
                elif on_stack[v]:  # Node v is part of the current SCC
                    low_link[u] = min(low_link[u], discovery_time[v])

                # Update low-link value in bookkeeping
                update_bookkeeping(u, discovery_time[u], low_link[u])
                self.wait(0.5)

            # Initialize scc variable outside the if block
            scc = []
            # If u is a root node, create an SCC
            if low_link[u] == discovery_time[u]:
                while stack:
                    node = stack.pop()
                    on_stack[node] = False
                    scc.append(node)
                    highlight_node(node, GREEN)  # Highlight the node as part of an SCC
                    self.wait(0.3)
                    if node == u:
                        break
                sccs.append(scc)
                self.wait(1)

            # Reset the color to blue only if the node is not part of an SCC
            if u not in scc:
                highlight_node(u, BLUE)

        # Run Tarjan's algorithm on each unvisited node
        for node in G.nodes():
            if discovery_time[node] is None:
                tarjan(node)

        # Final SCC Display
        self.wait(1)
        for scc in sccs:
            scc_text = Text(f"SCC: {scc}", font_size=24).to_edge(DOWN)
            self.play(Write(scc_text))
            self.wait(1)
            self.play(FadeOut(scc_text))

        # End scene
        self.wait(2)
