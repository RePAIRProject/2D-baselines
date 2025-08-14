"""
Mock Springs Server - Bypasses the external server dependency with geometric simulation
"""
import numpy as np
import math
from shapely import Polygon, Point
from shapely import affinity
from src.assembler import rigid_transformations
from src import shared_parameters


class MockSpringsSimulator:
    """Simple geometric mock that replaces the springs physics server"""
    
    def simulate(self, matings, fixed_rotation={}, **kwargs):
        """
        Mock simulation that performs basic geometric positioning
        
        Args:
            matings: List of mating dictionaries with structure:
                {
                    "firstPiece": "piece_id",
                    "firstPieceLocalCoords": [x, y],
                    "secondPiece": "piece_id", 
                    "secondPieceLocalCoords": [x, y]
                }
            fixed_rotation: Dict of piece rotations
                {
                    "piece_id": {"initialAngleRadians": angle}
                }
        
        Returns:
            Response dict matching server format:
            {
                "piecesFinalCoords": [{"pieceId": "...", "coordinates": [[x,y], ...]}],
                "piecesFinalTransformations": [{"pieceId": "...", "rotationRadians": r, "translateVectorX": x, "translateVectorY": y}]
            }
        """
        
        # Collect all unique pieces involved
        pieces_involved = set()
        for mating in matings:
            pieces_involved.add(mating["firstPiece"])
            pieces_involved.add(mating["secondPiece"])
        
        # Initialize response structure
        response = {
            "piecesFinalCoords": [],
            "piecesFinalTransformations": []
        }
        
        # Process each piece
        piece_positions = {}  # Track final positions
        
        for i, piece_name in enumerate(pieces_involved):
            # Get the piece object
            piece = self._get_piece_by_name(piece_name)
            if piece is None:
                print(f"Warning: Could not find piece {piece_name}")
                continue
            
            # Get original polygon
            original_polygon = piece.get_polygon()
            
            # Apply fixed rotation if specified
            rotation_angle = 0.0
            if piece_name in fixed_rotation:
                rotation_angle = fixed_rotation[piece_name]["initialAngleRadians"]
            
            # Start with original coordinates
            coords = list(original_polygon.exterior.coords[:-1])  # Remove duplicate last point
            
            # Apply rotation around centroid
            if rotation_angle != 0:
                centroid = original_polygon.centroid
                rotated_polygon = affinity.rotate(original_polygon, 
                                                math.degrees(rotation_angle), 
                                                origin=(centroid.x, centroid.y))
                coords = list(rotated_polygon.exterior.coords[:-1])
            
            # Simple positioning: spread pieces out to avoid major overlaps
            # This is a basic heuristic - real physics would be more sophisticated
            offset_x = i * 100  # Simple horizontal spacing
            offset_y = 0
            
            # Apply translation
            translated_coords = [[x + offset_x, y + offset_y] for x, y in coords]
            
            # Store results
            piece_positions[piece_name] = {
                "coordinates": translated_coords,
                "rotation": rotation_angle,
                "translation": (offset_x, offset_y)
            }
            
            # Add to response
            response["piecesFinalCoords"].append({
                "pieceId": piece_name,
                "coordinates": translated_coords
            })
            
            response["piecesFinalTransformations"].append({
                "pieceId": piece_name,
                "rotationRadians": rotation_angle,
                "translateVectorX": float(offset_x),
                "translateVectorY": float(offset_y)
            })
        
        # Optional: Try to align mating points (basic implementation)
        # This could be enhanced to actually move pieces to align their mating points
        self._align_mating_points(matings, piece_positions, response)
        
        return response
    
    def _get_piece_by_name(self, piece_name):
        """Get piece object by name from shared parameters"""
        # Try to find piece by full name first
        if piece_name in shared_parameters.active_pieces:
            return shared_parameters.active_pieces[piece_name]
        
        # Try to find by piece ID (without _intact_mesh suffix)
        piece_id = piece_name.replace("_intact_mesh", "")
        if piece_id in shared_parameters.active_pieces:
            return shared_parameters.active_pieces[piece_id]
        
        # Try all pieces and match by get_full_name()
        for piece in shared_parameters.active_pieces.values():
            if piece.get_full_name() == piece_name:
                return piece
        
        return None
    
    def _align_mating_points(self, matings, piece_positions, response):
        """
        Basic mating point alignment - adjusts piece positions to bring mating points closer
        This is a simplified version of what the physics server would do
        """
        for mating in matings:
            first_piece = mating["firstPiece"]
            second_piece = mating["secondPiece"]
            
            if first_piece not in piece_positions or second_piece not in piece_positions:
                continue
            
            # Get mating points in local coordinates
            first_point = mating["firstPieceLocalCoords"]
            second_point = mating["secondPieceLocalCoords"]
            
            # For simplicity, just move the second piece toward the first piece
            # A more sophisticated approach would solve for optimal positioning
            
            # Calculate desired translation to align mating points
            first_coords = piece_positions[first_piece]["coordinates"]
            second_coords = piece_positions[second_piece]["coordinates"]
            
            # Find the actual mating points in world coordinates
            # This is a simplified lookup - real implementation would transform local to world coords
            try:
                # Simple heuristic: find closest points to the specified local coordinates
                first_world_point = self._find_closest_point(first_coords, first_point)
                second_world_point = self._find_closest_point(second_coords, second_point)
                
                # Calculate offset needed
                offset_x = first_world_point[0] - second_world_point[0]
                offset_y = first_world_point[1] - second_world_point[1]
                
                # Apply offset to second piece (simple approach)
                for i, coord in enumerate(second_coords):
                    second_coords[i] = [coord[0] + offset_x, coord[1] + offset_y]
                
                # Update the response
                for coord_entry in response["piecesFinalCoords"]:
                    if coord_entry["pieceId"] == second_piece:
                        coord_entry["coordinates"] = second_coords
                        break
                
                # Update translation in transformations
                for trans_entry in response["piecesFinalTransformations"]:
                    if trans_entry["pieceId"] == second_piece:
                        trans_entry["translateVectorX"] += offset_x
                        trans_entry["translateVectorY"] += offset_y
                        break
                        
            except Exception as e:
                # If alignment fails, just continue - the basic positioning will still work
                print(f"Warning: Failed to align mating points for {first_piece}-{second_piece}: {e}")
                continue
    
    def _find_closest_point(self, coords, target_point):
        """Find the coordinate point closest to the target"""
        min_dist = float('inf')
        closest_point = coords[0]
        
        for coord in coords:
            dist = ((coord[0] - target_point[0])**2 + (coord[1] - target_point[1])**2)**0.5
            if dist < min_dist:
                min_dist = dist
                closest_point = coord
        
        return closest_point


# Global mock instance
mock_simulator = MockSpringsSimulator()