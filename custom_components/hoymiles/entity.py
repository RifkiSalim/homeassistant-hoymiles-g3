"""Base entity for Hoymiles."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import HoymilesCoordinator


class HoymilesEntity(CoordinatorEntity[HoymilesCoordinator]):
    """Shared device info for Hoymiles entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: HoymilesCoordinator, register_key: str) -> None:
        super().__init__(coordinator)
        self._register_key = register_key

    @property
    def device_info(self) -> DeviceInfo:
        info = self.coordinator.inverter_info
        model = info.inverter_model if info else "G3 Hybrid"
        data = self.coordinator.data or {}
        sw = data.get("powerdsp_fm_ver")
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name=f"Hoymiles {model}",
            manufacturer=MANUFACTURER,
            model=model,
            sw_version=str(sw) if sw is not None else None,
            suggested_area="Garage",
        )
