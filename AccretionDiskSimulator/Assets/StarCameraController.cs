using UnityEngine;

public class StarCameraController : MonoBehaviour
{
    public GameObject star; // The star object to follow
    public float zoomSpeed = 10.0f; // Speed of zooming in and out
    public float minZoomDistance = 5.0f; // Minimum distance from the star
    public float maxZoomDistance = 100.0f; // Maximum distance from the star
    public float rotationSpeed = 5.0f; // Speed of rotation when dragging the mouse
    public float smoothTime = 0.3f; // Time for smooth damping

    private Vector3 offset; // Initial offset between the camera and the star
    private Vector3 velocity = Vector3.zero; // Velocity for smooth damping
    private bool isDragging = false; // Whether the mouse is being dragged
    private Vector3 lastMousePosition; // Last recorded mouse position

    void Start()
    {
        if (star == null)
        {
            Debug.LogError("Star not assigned to StarCameraController!");
            return;
        }

        // Calculate the initial offset between the camera and the star
        offset = transform.position - star.transform.position;
    }

    void LateUpdate()
    {
        if (star == null) return;

        // Handle mouse drag for rotation
        HandleMouseDrag();

        // Calculate the target position for the camera
        Vector3 targetPosition = star.transform.position + offset;

        // Smoothly move the camera to the target position
        transform.position = Vector3.SmoothDamp(transform.position, targetPosition, ref velocity, smoothTime);

        // Make the camera look at the star
        transform.LookAt(star.transform);

        // Handle zooming
        HandleZoom();
    }

    void HandleMouseDrag()
    {
        // Check if the left mouse button is pressed
        if (Input.GetMouseButtonDown(0))
        {
            isDragging = true;
            lastMousePosition = Input.mousePosition;
        }
        else if (Input.GetMouseButtonUp(0))
        {
            isDragging = false;
        }

        // If dragging, rotate the camera around the star
        if (isDragging)
        {
            Vector3 deltaMouse = Input.mousePosition - lastMousePosition;

            // Rotate around the star based on mouse movement
            float rightAscensionDelta = deltaMouse.x * rotationSpeed * Time.deltaTime;
            float altitudeDelta = -deltaMouse.y * rotationSpeed * Time.deltaTime;

            // Rotate the offset vector around the star
            offset = Quaternion.Euler(0, rightAscensionDelta, 0) * offset; // Rotate around Y axis (right ascension)
            offset = Quaternion.AngleAxis(altitudeDelta, transform.right) * offset; // Rotate around X axis (altitude)

            // Update the last mouse position
            lastMousePosition = Input.mousePosition;
        }
    }

    void HandleZoom()
    {
        float scroll = Input.GetAxis("Mouse ScrollWheel");
        if (scroll != 0)
        {
            // Adjust the offset based on the scroll input
            offset -= offset.normalized * scroll * zoomSpeed;

            // Clamp the offset magnitude to stay within min and max zoom distances
            float currentDistance = offset.magnitude;
            currentDistance = Mathf.Clamp(currentDistance, minZoomDistance, maxZoomDistance);
            offset = offset.normalized * currentDistance;
        }
    }
}