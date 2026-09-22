"""Sensor platform for Hoymiles."""

from __future__ import annotations

from dataclasses import dataclass

from hoymiles_g3_modbus_tcp.registers import Register
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfApparentPower,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfReactivePower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_INCLUDE_DIAGNOSTICS,
    CONF_INCLUDE_GENERATOR,
    CONF_INCLUDE_SETTINGS,
    CONF_SENSOR_PROFILE,
    DOMAIN,
    PROFILE_STANDARD,
    iter_exposed_registers,
)
from .coordinator import HoymilesCoordinator
from .entity import HoymilesEntity


def _device_class(reg: Register) -> SensorDeviceClass | None:
    unit = reg.unit
    if unit == "V":
        return SensorDeviceClass.VOLTAGE
    if unit == "A":
        return SensorDeviceClass.CURRENT
    if unit == "W":
        return SensorDeviceClass.POWER
    if unit == "Hz":
        return SensorDeviceClass.FREQUENCY
    if unit == "kWh":
        return SensorDeviceClass.ENERGY
    if unit == "Var":
        return SensorDeviceClass.REACTIVE_POWER
    if unit == "VA":
        return SensorDeviceClass.APPARENT_POWER
    if unit == "%" and "soc" in reg.key:
        return SensorDeviceClass.BATTERY
    if reg.key.endswith("_temp") or unit == "°C":
        return SensorDeviceClass.TEMPERATURE
    return None


def _state_class(reg: Register) -> SensorStateClass | None:
    if reg.unit in ("W", "V", "A", "Hz", "Var", "VA"):
        return SensorStateClass.MEASUREMENT
    if reg.unit == "kWh" and ("today" in reg.key or "lifetime" in reg.key or "energy" in reg.key):
        return SensorStateClass.TOTAL_INCREASING
    if reg.key.endswith("_soc"):
        return SensorStateClass.MEASUREMENT
    return None


def _native_unit(reg: Register) -> str | None:
    mapping = {
        "V": UnitOfElectricPotential.VOLT,
        "A": UnitOfElectricCurrent.AMPERE,
        "W": UnitOfPower.WATT,
        "Hz": UnitOfFrequency.HERTZ,
        "kWh": UnitOfEnergy.KILO_WATT_HOUR,
        "Var": UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
        "VA": UnitOfApparentPower.VOLT_AMPERE,
        "%": PERCENTAGE,
        "°C": UnitOfTemperature.CELSIUS,
    }
    return mapping.get(reg.unit or "", reg.unit)


@dataclass(frozen=True, kw_only=True)
class HoymilesSensorEntityDescription(SensorEntityDescription):
    register_key: str


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HoymilesCoordinator = hass.data[DOMAIN][entry.entry_id]
    info = coordinator.inverter_info
    if info is None:
        return

    profile = entry.options.get(CONF_SENSOR_PROFILE, entry.data.get(CONF_SENSOR_PROFILE, PROFILE_STANDARD))
    registers = iter_exposed_registers(
        profile=profile,
        include_settings=entry.options.get(
            CONF_INCLUDE_SETTINGS, entry.data.get(CONF_INCLUDE_SETTINGS, False)
        ),
        include_generator=entry.options.get(
            CONF_INCLUDE_GENERATOR, entry.data.get(CONF_INCLUDE_GENERATOR, False)
        ),
        include_diagnostics=entry.options.get(
            CONF_INCLUDE_DIAGNOSTICS, entry.data.get(CONF_INCLUDE_DIAGNOSTICS, True)
        ),
        has_battery=info.has_battery,
        has_grid_meter=info.has_grid_meter,
        pv_mppt_count=info.pv_mppt_count,
    )

    entities = []
    for reg in registers:
        desc = HoymilesSensorEntityDescription(
            key=reg.key,
            register_key=reg.key,
            name=reg.label,
            native_unit_of_measurement=_native_unit(reg),
            device_class=_device_class(reg),
            state_class=_state_class(reg),
        )
        entities.append(HoymilesSensorEntity(coordinator, reg, desc))
    async_add_entities(entities)


class HoymilesSensorEntity(HoymilesEntity, SensorEntity):
    """Modbus register exposed as a sensor."""

    entity_description: HoymilesSensorEntityDescription

    def __init__(
        self,
        coordinator: HoymilesCoordinator,
        register: Register,
        description: HoymilesSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, register.key)
        self.entity_description = description
        self._register = register
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{register.key}"

    @property
    def native_value(self):
        value = self.coordinator.data.get(self._register.key) if self.coordinator.data else None
        if value is None:
            return None
        if isinstance(value, list):
            return ", ".join(value) if value else None
        return value

    @property
    def available(self) -> bool:
        if not super().available:
            return False
        return not self.coordinator.inverter.is_stale(self._register.key)
