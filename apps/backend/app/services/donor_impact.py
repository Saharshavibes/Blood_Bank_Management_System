import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.blood_bag import BloodBag
from app.models.enums import BloodBagStatus
from app.schemas.impact import DonorImpactRead, DonorMilestone, DonorTrendPoint


DONOR_IMPACT_STATUSES = [
    BloodBagStatus.COLLECTED,
    BloodBagStatus.TESTED,
    BloodBagStatus.AVAILABLE,
    BloodBagStatus.RESERVED,
    BloodBagStatus.ISSUED,
    BloodBagStatus.TRANSFUSED,
]

DONOR_MILESTONES = [
    (450, "First Lifeline"),
    (900, "Bronze Lifeline"),
    (1800, "Silver Lifeline"),
    (3600, "Gold Lifeline"),
    (5400, "Platinum Lifeline"),
]


def _recent_month_slots(count: int = 6) -> list[tuple[str, str]]:
    now = datetime.now(UTC)
    year = now.year
    month = now.month
    slots: list[tuple[str, str]] = []

    for offset in range(count - 1, -1, -1):
        month_index = month - offset
        slot_year = year
        while month_index <= 0:
            slot_year -= 1
            month_index += 12

        key = f"{slot_year:04d}-{month_index:02d}"
        label = datetime(slot_year, month_index, 1).strftime("%b %Y")
        slots.append((key, label))

    return slots


def build_donor_impact(db: Session, donor_id: uuid.UUID) -> DonorImpactRead:
    bags = db.scalars(
        select(BloodBag)
        .where(
            BloodBag.donor_id == donor_id,
            BloodBag.status.in_(DONOR_IMPACT_STATUSES),
        )
        .order_by(BloodBag.collection_date.asc())
    ).all()

    total_volume_ml = sum(item.volume_ml for item in bags)
    total_donations = len(bags)
    lives_impacted_estimate = int((total_volume_ml / 450) * 3) if total_volume_ml > 0 else 0

    cumulative_volume = 0
    milestone_achieved_at: dict[int, datetime] = {}
    for bag in bags:
        cumulative_volume += bag.volume_ml
        for target_volume, _ in DONOR_MILESTONES:
            if target_volume not in milestone_achieved_at and cumulative_volume >= target_volume:
                milestone_achieved_at[target_volume] = bag.collection_date

    milestones = [
        DonorMilestone(
            title=title,
            target_volume_ml=target_volume,
            achieved=total_volume_ml >= target_volume,
            achieved_at=milestone_achieved_at.get(target_volume),
        )
        for target_volume, title in DONOR_MILESTONES
    ]

    current_badge = "New Donor"
    for target_volume, title in DONOR_MILESTONES:
        if total_volume_ml >= target_volume:
            current_badge = title

    next_milestone = next((item for item in DONOR_MILESTONES if total_volume_ml < item[0]), None)
    next_milestone_volume_ml = next_milestone[0] if next_milestone else None
    next_badge = next_milestone[1] if next_milestone else None

    month_slots = _recent_month_slots()
    trend_buckets = {
        key: {
            "month": label,
            "volume_ml": 0,
            "donations": 0,
        }
        for key, label in month_slots
    }

    for bag in bags:
        key = f"{bag.collection_date.year:04d}-{bag.collection_date.month:02d}"
        if key in trend_buckets:
            trend_buckets[key]["volume_ml"] += bag.volume_ml
            trend_buckets[key]["donations"] += 1

    trends = [
        DonorTrendPoint(
            month=trend_buckets[key]["month"],
            volume_ml=trend_buckets[key]["volume_ml"],
            donations=trend_buckets[key]["donations"],
        )
        for key, _ in month_slots
    ]

    return DonorImpactRead(
        donor_id=donor_id,
        total_volume_ml=total_volume_ml,
        total_donations=total_donations,
        lives_impacted_estimate=lives_impacted_estimate,
        current_badge=current_badge,
        next_badge=next_badge,
        next_milestone_volume_ml=next_milestone_volume_ml,
        trends=trends,
        milestones=milestones,
    )