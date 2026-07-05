TEMPLATES = [
    {
        "title": "Product Launch Copywriter",
        "category": "Marketing",
        "description": "Create high-impact landing page copy for new products.",
        "prompt": "You are a world-class copywriter specializing in digital product launches. Write a persuasive landing page copy for [Product Name] that addresses the target audience [Audience] and emphasizes [Primary Benefit/USP]. Ensure you include a compelling hook, three feature-to-benefit breakdowns, user objection handling, and a clear call-to-action (CTA). Tone should be [Tone, e.g., confident and friendly]."
    },
    {
        "title": "SEO Blog Generator",
        "category": "Marketing",
        "description": "Generate an SEO-optimized outline and blog draft.",
        "prompt": "Act as an SEO content specialist. Draft an engaging blog post about [Topic] targeting the keywords [Keywords]. Outline the post using H2 and H3 subheadings. The introduction should hook the reader, the body paragraphs should include structural bullet points for readability, and the conclusion should invite user engagement. Keep the tone [Tone, e.g., authoritative yet accessible] and aim for a word count of [Word Count, e.g., 1000 words]."
    },
    {
        "title": "Code Refactoring & Explainer",
        "category": "Coding",
        "description": "Refactor code for performance and readability, with step-by-step comments.",
        "prompt": "You are an expert software engineer. Review the following code snippet: \n\n```[Language]\n[CodeSnippet]\n```\n\nPerform the following tasks:\n1. Refactor the code for improved readability, efficiency, and adherence to [Language] best practices.\n2. Identify any potential bugs, edge cases, or memory leaks.\n3. Add clean inline docstrings and comments.\n4. Provide a brief explanation of the performance enhancements made."
    },
    {
        "title": "Unit Test Creator",
        "category": "Coding",
        "description": "Write comprehensive unit tests covering edge cases.",
        "prompt": "Act as an expert QA automation engineer. Write a set of comprehensive unit tests for the following [Language] function using the [Testing Framework, e.g., pytest, Jest] library:\n\n```[Language]\n[FunctionCode]\n```\n\nEnsure you test:\n- Typical happy-path scenarios.\n- Edge cases (null inputs, boundary limits, empty collections).\n- Error handling and expected exception raising."
    },
    {
        "title": "UI Component Spec Sheet",
        "category": "Design",
        "description": "Describe design specs, states, and accessibility details for a UI element.",
        "prompt": "Act as a Senior UI/UX Designer. Create a comprehensive design specification sheet for a [Component, e.g., Date Picker dropdown]. Include definitions for:\n1. Visual styles (layout, spacing, padding, hover/focus/active states).\n2. Interactive states (disabled, error, loading).\n3. Screen responsiveness rules.\n4. Accessibility requirements (ARIA roles, keyboard navigation, color contrast targets)."
    },
    {
        "title": "User Persona Profiler",
        "category": "UX",
        "description": "Build a target user persona sheet including pain points and motivators.",
        "prompt": "Act as a Lead UX Researcher. Build a detailed user persona profile for a [Target Product/App] user. Include the following sections:\n- Demographics (Name, Age, Occupation, Tech Savviness).\n- Behaviors & Goals (What are they trying to achieve?).\n- Core Pain Points (What currently frustrates them?).\n- Direct Quotation (A representative phrase summarizing their mindset).\n- Technical Environment (Devices, screen dimensions, preferred apps)."
    },
    {
        "title": "Scientific Paper Summarizer",
        "category": "Research",
        "description": "Extract methodology, key findings, and limitations from paper drafts.",
        "prompt": "Act as a research analyst. Summarize the following academic manuscript text:\n\n[ManuscriptText]\n\nAnalyze and extract:\n1. Core hypothesis or objective.\n2. Methodology utilized (data collection, cohort size, statistical tests).\n3. Key quantitative results.\n4. Identified limitations and future directions. Format the output in bullet points under clear Markdown headings."
    },
    {
        "title": "Engaging Novel Opening",
        "category": "Writing",
        "description": "Draft a hook and opening chapter outline for a fiction novel.",
        "prompt": "You are an award-winning novelist. Write the opening scene (approx. 500 words) for a story in the [Genre] genre. The plot centers around [Main Conflict]. Introduce the protagonist [Character Name] and establish a sense of mystery or urgency immediately. Use rich sensory details, showing rather than telling, and hook the reader's curiosity."
    },
    {
        "title": "Socratic Lesson Planner",
        "category": "Education",
        "description": "Create a lesson plan that teaches concepts via guided questioning.",
        "prompt": "Act as a teacher employing the Socratic method. Outline a lesson plan to teach [Subject/Concept] to [Grade Level, e.g., High School students]. Structure the lesson around a series of 5-7 open-ended questions designed to lead the student to discover the core concept themselves. For each question, anticipate potential misconceptions and write guidance prompts to help nudge them back on track."
    },
    {
        "title": "Pitch Deck Outline Builder",
        "category": "Business",
        "description": "Draft a slide-by-slide storyline for a startup pitch deck.",
        "prompt": "Act as a venture capital consultant. Outline a compelling 10-slide pitch deck storyline for a startup in the [Industry] sector named [Startup Name]. For each slide (Problem, Solution, Market Size, Traction, etc.), define:\n1. Core message or single headline.\n2. Key data points/metrics to feature.\n3. Supporting visuals or chart recommendations."
    },
    {
        "title": "Midjourney Prompt Artisan",
        "category": "Image Generation",
        "description": "Convert basic concepts into high-detail prompt structures for generative art.",
        "prompt": "Act as an expert Midjourney Prompt Engineer. Transform the basic concept '[Art Concept]' into a highly-detailed prompt. Include:\n- Subject description (clothing, expression, posture).\n- Environment, setting, and lighting dynamics (e.g., volumetric lighting, golden hour).\n- Artistic style, camera type, lens focal length, and rendering details (e.g., cinematic, 8k, photorealistic, Unreal Engine 5 render).\n- Aspect ratio parameters (e.g., --ar 16:9) and version tag (e.g., --v 6.0)."
    }
]

def search_templates(query: str = "", category: str = "All") -> list:
    """Filters the template database based on search query and category."""
    filtered = TEMPLATES
    if category != "All":
        filtered = [t for t in filtered if t["category"] == category]
    
    if query:
        q = query.lower()
        filtered = [
            t for t in filtered 
            if q in t["title"].lower() or q in t["description"].lower() or q in t["prompt"].lower()
        ]
        
    return filtered

def get_categories() -> list:
    """Returns a list of all unique categories in the template database."""
    categories = sorted(list(set(t["category"] for t in TEMPLATES)))
    return ["All"] + categories
