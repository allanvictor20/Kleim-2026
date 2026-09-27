"""External services are reached through interfaces with fakes (NFR-10)."""
from __future__ import annotations

import pytest

from app.integrations.maps.fake import StraightLineMapsClient, haversine_metres
from app.integrations.maps.interface import Point
from app.integrations.payments.fake import SimulatedPaymentsClient
from app.integrations.payments.interface import ChargeRequest
from app.integrations.sms.fake import ConsoleSmsClient
from app.integrations.storage.fake import LocalStorageClient
from app.integrations.storage.interface import MAX_UPLOAD_BYTES

# Kampala city centre and Ntinda, roughly 5 km apart.
CITY_CENTRE = Point(longitude=32.5825, latitude=0.3476)
NTINDA = Point(longitude=32.6103, latitude=0.3663)


def test_console_sms_keeps_an_outbox_so_tests_can_assert_on_otp() -> None:
    client = ConsoleSmsClient()

    client.send("+256700000001", "Your Kleim code is 123456")

    assert len(client.outbox) == 1
    assert client.outbox[0].to == "+256700000001"
    assert "123456" in client.outbox[0].body


def test_straight_line_distance_is_plausible_for_kampala() -> None:
    metres = haversine_metres(CITY_CENTRE, NTINDA)
    assert 3_000 < metres < 5_000


def test_route_applies_the_road_factor_the_sdd_prescribes() -> None:
    straight = haversine_metres(CITY_CENTRE, NTINDA)

    route = StraightLineMapsClient().route(CITY_CENTRE, NTINDA)

    assert route.distance_metres == round(straight * 1.3)
    assert route.estimated is True
    assert route.duration_seconds > 0


def test_identical_points_are_zero_distance() -> None:
    route = StraightLineMapsClient().route(CITY_CENTRE, CITY_CENTRE)
    assert route.distance_metres == 0


def test_simulated_charge_stays_pending_until_it_is_resolved() -> None:
    """The MVP moves no live money (SDD section 2.2): an operator settles it."""
    client = SimulatedPaymentsClient()

    result = client.charge(
        ChargeRequest(amount=45_000, phone="+256700000001", method="mtn_momo", reference="o-1")
    )

    assert result.status == "pending"
    assert result.provider_reference.startswith("sim-")
    assert client.charges[0].amount == 45_000


def test_local_storage_keys_are_random_and_typed() -> None:
    client = LocalStorageClient()

    first = client.sign_upload("products", "image/jpeg")
    second = client.sign_upload("products", "image/jpeg")

    assert first.storage_key != second.storage_key
    assert first.storage_key.startswith("products/")
    assert first.storage_key.endswith(".jpg")


def test_local_storage_refuses_a_type_the_sdd_disallows() -> None:
    with pytest.raises(ValueError):
        LocalStorageClient().sign_upload("products", "image/gif")


def test_upload_limit_matches_the_sdd() -> None:
    assert MAX_UPLOAD_BYTES == 5 * 1024 * 1024


def test_public_url_can_request_a_narrower_image_for_low_bandwidth() -> None:
    url = LocalStorageClient().public_url("products/abc.jpg", width=400)
    assert url.endswith("?w=400")
