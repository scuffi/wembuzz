"""Layout class for managing component regions and organization."""

from typing import Dict, List, Optional
from ..utils import Region, Position
from ..components.base import Component


class Layout:
    """Manages component regions and organization within a display."""

    def __init__(self, width: int, height: int):
        """
        Initialize a layout.

        Args:
            width: Total width of the layout
            height: Total height of the layout
        """
        self.width = width
        self.height = height
        self.regions: Dict[str, Region] = {}
        self._components: Dict[str, Component] = {}

    def define_region(self, name: str, region: Region) -> None:
        """
        Define a named region in the layout.

        Args:
            name: Unique name for the region
            region: The region definition
        """
        # Validate region fits within layout
        if region.x < 0 or region.y < 0:
            raise ValueError(f"Region {name} has negative coordinates")
        if region.x + region.width > self.width:
            raise ValueError(f"Region {name} extends beyond layout width")
        if region.y + region.height > self.height:
            raise ValueError(f"Region {name} extends beyond layout height")

        self.regions[name] = region

    def get_region(self, name: str) -> Optional[Region]:
        """Get a region by name."""
        return self.regions.get(name)

    def add_component(self, name: str, component: Component, region_name: Optional[str] = None) -> None:
        """
        Add a component to the layout.

        Args:
            name: Unique name for the component
            component: The component to add
            region_name: Optional region name to bind component to
        """
        if region_name:
            region = self.get_region(region_name)
            if not region:
                raise ValueError(f"Region {region_name} not found")
            # Update component to use the layout region
            component.set_region(region)

        self._components[name] = component

    def get_component(self, name: str) -> Optional[Component]:
        """Get a component by name."""
        return self._components.get(name)

    def remove_component(self, name: str) -> None:
        """Remove a component from the layout."""
        if name in self._components:
            del self._components[name]

    def get_all_components(self) -> Dict[str, Component]:
        """Get all components in the layout."""
        return self._components.copy()

    def update_component_region(self, name: str, region_name: str) -> None:
        """Update a component's region by binding it to a layout region."""
        component = self.get_component(name)
        if not component:
            raise ValueError(f"Component {name} not found")

        region = self.get_region(region_name)
        if not region:
            raise ValueError(f"Region {region_name} not found")

        component.set_region(region)

    def split_horizontal(self, name: str, *sizes: int) -> List[str]:
        """
        Split a region horizontally into multiple sub-regions.

        Args:
            name: Name of the region to split
            *sizes: Widths of the sub-regions (can use -1 for remaining space)

        Returns:
            List of new region names
        """
        region = self.get_region(name)
        if not region:
            raise ValueError(f"Region {name} not found")

        # Calculate total fixed size
        total_fixed = sum(s for s in sizes if s > 0)
        remaining = region.width - total_fixed
        num_flex = sum(1 for s in sizes if s < 0)

        if num_flex > 0:
            flex_size = remaining // num_flex
        else:
            flex_size = 0

        new_regions = []
        x_offset = region.x

        for i, size in enumerate(sizes):
            if size < 0:
                width = flex_size
            else:
                width = size

            sub_name = f"{name}_{i}"
            sub_region = Region(x_offset, region.y, width, region.height)
            self.define_region(sub_name, sub_region)
            new_regions.append(sub_name)
            x_offset += width

        return new_regions

    def split_vertical(self, name: str, *sizes: int) -> List[str]:
        """
        Split a region vertically into multiple sub-regions.

        Args:
            name: Name of the region to split
            *sizes: Heights of the sub-regions (can use -1 for remaining space)

        Returns:
            List of new region names
        """
        region = self.get_region(name)
        if not region:
            raise ValueError(f"Region {name} not found")

        # Calculate total fixed size
        total_fixed = sum(s for s in sizes if s > 0)
        remaining = region.height - total_fixed
        num_flex = sum(1 for s in sizes if s < 0)

        if num_flex > 0:
            flex_size = remaining // num_flex
        else:
            flex_size = 0

        new_regions = []
        y_offset = region.y

        for i, size in enumerate(sizes):
            if size < 0:
                height = flex_size
            else:
                height = size

            sub_name = f"{name}_{i}"
            sub_region = Region(region.x, y_offset, region.width, height)
            self.define_region(sub_name, sub_region)
            new_regions.append(sub_name)
            y_offset += height

        return new_regions
