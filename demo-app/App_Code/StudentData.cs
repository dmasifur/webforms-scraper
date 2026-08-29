using System;
using System.Collections.Generic;
using System.Linq;

public class Student
{
    public string StudentId { get; set; }
    public string FirstName { get; set; }
    public string LastName { get; set; }
    public string Campus { get; set; }
    public string Course { get; set; }
    public DateTime EnrolmentDate { get; set; }
    public string Status { get; set; }

    public string Email { get; set; }
    public string Phone { get; set; }
    public DateTime DateOfBirth { get; set; }
    public string Address { get; set; }
    public string EmergencyContact { get; set; }

    public string FullName
    {
        get { return FirstName + " " + LastName; }
    }
}

/// <summary>
/// Deterministic synthetic dataset. Fixed seed means the committed .xlsx is
/// byte-stable and the test fixtures never drift.
/// </summary>
public static class StudentData
{
    private const int Seed = 137;
    private const int RecordCount = 137;

    private static readonly string[] FirstNames = {
        "Amara", "Beatriz", "Caleb", "Dilnoza", "Elias", "Farida", "Gustavo", "Hana",
        "Idris", "Jiwoo", "Kofi", "Lucia", "Mateo", "Naila", "Omar", "Priya",
        "Quentin", "Rania", "Sundar", "Tomas", "Ulla", "Viktor", "Wanjiru", "Yusuf"
    };

    private static readonly string[] LastNames = {
        "Abbott", "Bianchi", "Castillo", "Duarte", "Eriksen", "Fontaine", "Grimaldi",
        "Haddad", "Ibrahim", "Jansen", "Kowalski", "Lindqvist", "Moreau", "Novak",
        "Okonkwo", "Pereira", "Quiroga", "Ramanathan", "Sorensen", "Tanaka"
    };

    private static readonly string[] CampusNames = {
        "Northbridge", "Eastgate", "Southpoint", "Westfield"
    };

    private static readonly string[] CourseNames = {
        "Certificate III in Business",
        "Certificate IV in Project Management",
        "Diploma of Information Technology",
        "Diploma of Leadership and Management",
        "Advanced Diploma of Accounting"
    };

    private static readonly string[] StatusNames = {
        "Active", "Deferred", "Completed", "Withdrawn"
    };

    private static readonly string[] StreetNames = {
        "Wattle", "Banksia", "Jacaranda", "Kurrajong", "Melaleuca", "Bottlebrush"
    };

    private static readonly List<Student> All = Build();

    private static List<Student> Build()
    {
        Random rng = new Random(Seed);
        List<Student> list = new List<Student>();

        for (int i = 0; i < RecordCount; i++)
        {
            string first = FirstNames[rng.Next(FirstNames.Length)];
            string last = LastNames[rng.Next(LastNames.Length)];

            Student s = new Student();
            s.StudentId = "STU-" + (10000 + i).ToString();
            s.FirstName = first;
            s.LastName = last;
            s.Campus = CampusNames[rng.Next(CampusNames.Length)];
            s.Course = CourseNames[rng.Next(CourseNames.Length)];
            s.EnrolmentDate = new DateTime(2023, 1, 1).AddDays(rng.Next(0, 900));
            s.Status = StatusNames[rng.Next(StatusNames.Length)];

            s.Email = (first + "." + last).ToLowerInvariant() + i.ToString() + "@example.edu";
            s.Phone = "04" + rng.Next(10, 99).ToString() + " "
                    + rng.Next(100, 999).ToString() + " "
                    + rng.Next(100, 999).ToString();
            s.DateOfBirth = new DateTime(1985, 1, 1).AddDays(rng.Next(0, 6500));
            s.Address = rng.Next(1, 199).ToString() + " "
                      + StreetNames[rng.Next(StreetNames.Length)] + " Street, "
                      + s.Campus;
            s.EmergencyContact = FirstNames[rng.Next(FirstNames.Length)] + " "
                               + last + " (04"
                               + rng.Next(10, 99).ToString() + " "
                               + rng.Next(100, 999).ToString() + " "
                               + rng.Next(100, 999).ToString() + ")";

            list.Add(s);
        }

        return list;
    }

    public static List<string> Campuses()
    {
        return CampusNames.OrderBy(c => c).ToList();
    }

    /// <summary>Server-side filter. Empty campus means no filter.</summary>
    public static List<Student> Query(string campus)
    {
        IEnumerable<Student> q = All;
        if (!string.IsNullOrEmpty(campus))
        {
            q = q.Where(s => s.Campus == campus);
        }
        return q.OrderBy(s => s.StudentId).ToList();
    }

    public static Student Find(string studentId)
    {
        return All.FirstOrDefault(s => s.StudentId == studentId);
    }

    public static int Count
    {
        get { return All.Count; }
    }
}