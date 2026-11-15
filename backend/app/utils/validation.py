from fastapi import HTTPException

def validate_coordinates(latitude: float, longitude: float):
    if not (-90.0 <= latitude <= 90.0):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid latitude {latitude}. Latitude must be within [-90.0, 90.0]."
        )
    if not (-180.0 <= longitude <= 180.0):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid longitude {longitude}. Longitude must be within [-180.0, 180.0]."
        )

def validate_year_range(start_year: int | None, end_year: int | None, min_year: int = 1880, max_year: int = 2030):
    if start_year is not None and start_year < min_year:
        raise HTTPException(
            status_code=400,
            detail=f"start_year {start_year} is below minimum recorded epoch ({min_year})."
        )
    if end_year is not None and end_year > max_year:
        raise HTTPException(
            status_code=400,
            detail=f"end_year {end_year} exceeds reasonable future boundary ({max_year})."
        )
    if start_year is not None and end_year is not None and start_year > end_year:
        raise HTTPException(
            status_code=400,
            detail=f"start_year ({start_year}) cannot be greater than end_year ({end_year})."
        )
