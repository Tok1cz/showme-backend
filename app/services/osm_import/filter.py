import logging
import osmium
from pathlib import Path
from typing import Dict, Set
import os

from app.core.settings import settings

logger = logging.getLogger(__name__)

# Filtering tag sets (should match your current logic)
TOURISM_VALUES = {"attraction", "monument", "memorial", "museum", "artwork", "viewpoint"}
NATURAL_VALUES = {"peak", "waterfall", "cliff", "bay", "cave_entrance"}
AMENITY_VALUES = {"restaurant", "pub", "cafe"}
SHOP_VALUES = {"brewery", "distillery"}

class FirstPassHandler(osmium.SimpleHandler):
    """Collect all attraction node/way/relation IDs and referenced node IDs."""
    def __init__(self, log_prefix=""):
        super().__init__()
        self.attraction_ways = []
        self.attraction_nodes = []
        self.attraction_relations = []
        self.referenced_node_ids = set()
        self.log_prefix = log_prefix

    def is_attraction(self, tags):
        if "historic" in tags or "heritage" in tags or "artwork_type" in tags:
            return True
        if tags.get("tourism") in TOURISM_VALUES:
            return True
        if tags.get("natural") in NATURAL_VALUES:
            return True
        if tags.get("amenity") in AMENITY_VALUES:
            return True
        if tags.get("shop") in SHOP_VALUES:
            return True
        return False

    def node(self, n):
        if self.is_attraction(n.tags):
            self.attraction_nodes.append(n.id)

    def way(self, w):
        if self.is_attraction(w.tags):
            self.attraction_ways.append(w.id)
            for n in w.nodes:
                self.referenced_node_ids.add(n.ref)

    def relation(self, r):
        if self.is_attraction(r.tags):
            self.attraction_relations.append(r.id)
            for m in r.members:
                if m.type == "n":
                    self.referenced_node_ids.add(m.ref)

class SecondPassWriter(osmium.SimpleHandler):
    """Write out all relevant nodes, ways, and relations to the filtered file."""
    def __init__(self, writer, node_ids: Set[int], way_ids: Set[int], relation_ids: Set[int], referenced_node_ids: Set[int]):
        super().__init__()
        self.writer = writer
        self.node_ids = set(node_ids) | set(referenced_node_ids)
        self.way_ids = set(way_ids)
        self.relation_ids = set(relation_ids)

    def node(self, n):
        if n.id in self.node_ids:
            self.writer.add_node(n)

    def way(self, w):
        if w.id in self.way_ids:
            self.writer.add_way(w)

    def relation(self, r):
        if r.id in self.relation_ids:
            self.writer.add_relation(r)

def filter_osm_file(input_path: Path, output_path: Path, log_prefix="") -> None:
    """Filter a single .osm.pbf file, keeping only attractions + refs."""
    logger.info("%sFiltering file: %s", log_prefix, input_path)
    # First pass: collect IDs
    fp_handler = FirstPassHandler(log_prefix)
    fp_handler.apply_file(str(input_path), locations=False)
    logger.info(
        "%sCollected: %d nodes, %d ways, %d relations, %d referenced nodes",
        log_prefix,
        len(fp_handler.attraction_nodes),
        len(fp_handler.attraction_ways),
        len(fp_handler.attraction_relations),
        len(fp_handler.referenced_node_ids),
    )
    # Second pass: write filtered file
    writer = osmium.SimpleWriter(str(output_path))
    sp_handler = SecondPassWriter(
        writer,
        fp_handler.attraction_nodes,
        fp_handler.attraction_ways,
        fp_handler.attraction_relations,
        fp_handler.referenced_node_ids,
    )
    sp_handler.apply_file(str(input_path), locations=False)
    writer.close()
    logger.info("%sFinished filtering file: %s", log_prefix, output_path)

def filter_osm_files(file_map: Dict[str, Path]) -> Dict[str, Path]:
    """
    Given a mapping of region -> raw .osm.pbf Path,
    filters each file and deletes the original if successful.
    Returns a mapping of region -> filtered .osm.pbf Path.
    """
    filtered_map: Dict[str, Path] = {}
    for region, in_path in file_map.items():
        log_prefix = "[%s] " % region
        out_path = in_path.parent / f"{region}-filtered.osm.pbf"
        try:
            filter_osm_file(in_path, out_path, log_prefix)
            filtered_map[region] = out_path
            # Remove original file only after successful filtering
            try:
                in_path.unlink()
                logger.info("%sDeleted original file: %s", log_prefix, in_path)
            except Exception as del_err:
                logger.warning("%sFailed to delete original: %s (%s)", log_prefix, in_path, del_err)
        except Exception as e:
            logger.error("%sFilter failed: %s", log_prefix, e)
            raise
    return filtered_map
