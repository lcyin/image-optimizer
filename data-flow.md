graph TD
    A[User  Interface] -->|Upload Image| B[Image Upload Service]
    B -->|Send Image Data| C[Backend API Flask]
    C -->|Process Image| D[Image Processing Service OpenCV]
    D -->|Adjust Image Quality| E[Image Quality Adjustment Algorithm]
    E -->|Return Processed Image| C
    C -->|Send Response| B
    B -->|Display Processed Image| A