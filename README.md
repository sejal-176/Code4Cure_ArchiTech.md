# 🏗️ ArchiTech: Vastu-Compliant Generative Architecture

<p align="center">
  <b>Automated Floor Plan Synthesis via Constraint-Based Operations Research</b>
  <br />
  <i>Bridging Traditional Vedic Principles with Modern Computational Geometry</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Google%20OR--Tools-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="OR-Tools" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind" />
  <img src="https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black" alt="Firebase" />
</p>

---

## 📌 Executive Summary

**ArchiTech** is an intelligent generative design engine that automates the creation of Vastu-compliant residential floor plans. By treating architectural requirements with **simple constraint-based logic and OR-Tools**, the application generates mathematically optimized 1BHK, 2BHK, and 3BHK layouts based on minimal inputs such as plot size and facing direction. It effectively bridges the gap between traditional architectural wisdom and practical, modern spatial design.

## 🛠️ Core Technology Stack

* **Logic Engine**: **Google OR-Tools** (Operations Research) for room allocation and furniture placement optimization.
* **Backend**: Python-based REST API managing the rule-engine and constraint solver.
* **Frontend**: React & TypeScript with Tailwind CSS for high-performance visualization.
* **Data Layer**: Firebase for secure user credentials and project history.
* **Storage**: Uploadstore for persistent storage of generated SVG layouts and analysis reports.

---

## ⚙️ System Architecture

ArchiTech utilizes a multi-stage pipeline to transform user constraints into architectural blueprints:

```mermaid
graph TD
    A[User Input: Plot Area, Facing, BHK] --> B[React Frontend]
    B --> C[Python REST API]
    subgraph Optimization Engine
    C --> D[Algorithm 1: Room Allocation]
    D --> E[Algorithm 2: Furniture Placement]
    end
    E --> F[SVG/Image Generator]
    F --> G[Interactive UI Visualization]
✨ Key Functional Modules
1. Generative Vastu Engine
Directional Zoning: Automates placement of puja rooms, kitchens, and entrances based on Vastu Shastra rules (e.g., NE for Puja, SE for Kitchen).

Standardized Layouts: Supports 1BHK, 2BHK, and 3BHK configurations with connected rooms and proper spatial flow.

Constraint Optimization: Uses Operations Research to solve for room dimensions while maintaining North arrow and dimension annotations.

2. Intelligent Furniture Mapping
Geometry-Aware Placement: Furniture is placed relative to room geometry rather than being randomized.

Room-Specific Rulesets: Logic adapts based on room type—handling living room seating, kitchen work triangles (stove, sink, platform), and bedroom clearance.

3. User & Design Management
Persistence: Secure user accounts with saved design history and layout management.

Deliverables: Automated generation of overall analysis reports and high-fidelity SVG exports.

📈 Progress
✅ Fully Implemented
Automated Vastu-compliant generation for 1-3 BHK layouts.

Rule-based furniture placement engine.

SVG/Image floor plan output with full annotations.

User dashboard with design history and report generation.

🚧 Work in Progress
Orientation Expansion: Currently supporting North and East entrances; developing support for South and West-facing plots while maintaining compliance.

Enhanced Scaling: Improving the extensibility of rule-based placement for irregular plot boundaries.

🔮 Future Scope
3D Visualization: Implementing immersive walkthroughs of generated plans.

Vastu Scoring: Priority-based rule weighting to provide a digital compliance score.

Commercial Expansion: Support for duplexes, villas, and commercial layouts.

🛠️ Project Setup
Clone the Repository

Bash
git clone [https://github.com/sejal-176/CodeForCure_ArchiTech.md.git](https://github.com/sejal-176/CodeForCure_ArchiTech.md.git)
Install Dependencies

Bash
cd ArchiTech
npm install
Launch Application

Bash
npm start
👨‍💻 Team Members
Team Code4Cure:

Aishwarya Jadhav (@AishVerse)

Rudrani Wadelkar (@rudrani29)

Shreya Kale (@Shreysk21)

Sejal Bodakhe (@sejal-176)
