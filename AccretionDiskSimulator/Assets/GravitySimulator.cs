using System.Collections.Generic;
using UnityEngine;

public class GravitySimulator : MonoBehaviour
{
    public GameObject star; // The central star object
    public GameObject planetPrefab; // Prefab for planets
    public int numberOfPlanets = 10; // Number of planets to generate
    public float minRadius = 5.0f; // Inner radius of the disk
    public float maxRadius = 20.0f; // Outer radius of the disk
    public float gravitationalConstant = 1.0f; // Scale factor for gravity

    private List<Rigidbody> bodies = new List<Rigidbody>(); // List to track all bodies (star and planets)
    private List<Rigidbody> planets = new List<Rigidbody>(); // List to track only planets

    void Start()
    {
        GeneratePlanets();
        AddStarToBodiesList();
    }

    void GeneratePlanets()
    {
        Rigidbody starRb = star.GetComponent<Rigidbody>();
        float starMass = starRb.mass;

        for (int i = 0; i < numberOfPlanets; i++)
        {
            // Random position in a disk
            float radius = Random.Range(minRadius, maxRadius);
            float angle = Random.Range(0, 2 * Mathf.PI);
            Vector3 position = new Vector3(radius * Mathf.Cos(angle), 0, radius * Mathf.Sin(angle));
            position += star.transform.position;

            // Instantiate planet
            GameObject planet = Instantiate(planetPrefab, position, Quaternion.identity);
            Rigidbody planetRb = planet.GetComponent<Rigidbody>();

            // Add the planet's Rigidbody to the lists
            bodies.Add(planetRb);
            planets.Add(planetRb);

            // Assign a random color to the planet
            Renderer planetRenderer = planet.GetComponent<Renderer>();
            if (planetRenderer != null)
            {
                planetRenderer.material.color = Random.ColorHSV();
            }

            // Calculate velocity for circular orbit
            float speed = Mathf.Sqrt(gravitationalConstant * starMass / radius);
            Vector3 velocityDirection = Vector3.Cross(position - star.transform.position, Vector3.up).normalized;
            Vector3 velocity = speed * velocityDirection;

            // Set the initial velocity of the planet
            planetRb.linearVelocity = velocity;

            // Add a collision handler to the planet
            planet.AddComponent<PlanetCollisionHandler>().Initialize(this);
        }
    }

    void AddStarToBodiesList()
    {
        // Add the star's Rigidbody to the list
        Rigidbody starRb = star.GetComponent<Rigidbody>();
        bodies.Add(starRb);
    }

    void FixedUpdate()
    {
        // Calculate gravitational forces between all pairs of bodies
        for (int i = 0; i < bodies.Count; i++)
        {
            for (int j = i + 1; j < bodies.Count; j++)
            {
                Rigidbody body1 = bodies[i];
                Rigidbody body2 = bodies[j];

                // Calculate the direction and distance between the two bodies
                Vector3 direction = body2.position - body1.position;
                float distance = direction.magnitude;

                // Avoid division by zero (if two bodies are exactly at the same position)
                if (distance == 0) continue;

                // Calculate the force magnitude using Newton's law of universal gravitation
                float forceMagnitude = gravitationalConstant * (body1.mass * body2.mass) / Mathf.Pow(distance, 2);

                // Calculate the force vector
                Vector3 force = direction.normalized * forceMagnitude;

                // Apply equal and opposite forces to both bodies
                body1.AddForce(force);
                body2.AddForce(-force);
            }
        }
    }

    // Method to handle planet collisions
    public void HandlePlanetCollision(Rigidbody planet1, Rigidbody planet2)
    {
        // Calculate the new mass
        float newMass = planet1.mass + planet2.mass;

        // Calculate the new velocity using conservation of momentum
        Vector3 newVelocity = (planet1.mass * planet1.linearVelocity + planet2.mass * planet2.linearVelocity) / newMass;

        // Calculate the new position as the center of mass
        Vector3 newPosition = (planet1.mass * planet1.position + planet2.mass * planet2.position) / newMass;

        // Destroy the two colliding planets
        bodies.Remove(planet1);
        bodies.Remove(planet2);
        planets.Remove(planet1);
        planets.Remove(planet2);
        Destroy(planet1.gameObject);
        Destroy(planet2.gameObject);

        // Create a new planet at the center of mass
        GameObject newPlanet = Instantiate(planetPrefab, newPosition, Quaternion.identity);
        Rigidbody newPlanetRb = newPlanet.GetComponent<Rigidbody>();
        newPlanetRb.mass = newMass;
        newPlanetRb.linearVelocity = newVelocity;

        // Assign a random color to the new planet
        Renderer newPlanetRenderer = newPlanet.GetComponent<Renderer>();
        if (newPlanetRenderer != null)
        {
            newPlanetRenderer.material.color = Random.ColorHSV();
        }

        // Add the new planet to the lists
        bodies.Add(newPlanetRb);
        planets.Add(newPlanetRb);

        // Add a collision handler to the new planet
        newPlanet.AddComponent<PlanetCollisionHandler>().Initialize(this);
    }

    // Method to handle planet-star collisions
    public void HandlePlanetStarCollision(Rigidbody planet)
    {
        // Increase the star's mass
        Rigidbody starRb = star.GetComponent<Rigidbody>();
        starRb.mass += planet.mass;

        // Destroy the planet
        bodies.Remove(planet);
        planets.Remove(planet);
        Destroy(planet.gameObject);
    }

    // Public method to check if a Rigidbody is a planet
    public bool IsPlanet(Rigidbody rb)
    {
        return planets.Contains(rb);
    }
}

// Script to handle planet collisions
public class PlanetCollisionHandler : MonoBehaviour
{
    private GravitySimulator gravitySimulator;

    public void Initialize(GravitySimulator simulator)
    {
        gravitySimulator = simulator;
    }

    private void OnCollisionEnter(Collision collision)
    {
        Rigidbody thisRb = GetComponent<Rigidbody>();
        Rigidbody otherRb = collision.collider.GetComponent<Rigidbody>();

        if (otherRb == null) return;

        // Check if the other object is a planet
        if (gravitySimulator.IsPlanet(otherRb))
        {
            gravitySimulator.HandlePlanetCollision(thisRb, otherRb);
        }
        // Check if the other object is the star
        else if (collision.collider.gameObject == gravitySimulator.star)
        {
            gravitySimulator.HandlePlanetStarCollision(thisRb);
        }
    }
}