"""
Image analysis for brand compliance using GPT-4 Vision.
"""
from openai import OpenAI
from typing import Dict, Any, Optional
import base64
from io import BytesIO
from PIL import Image
from config import settings
from rag.retrieval import retrieval_manager


class BrandAnalyzer:
    """Analyzes images for brand compliance using GPT-4 Vision."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    def analyze_image(
        self,
        image_data: bytes,
        image_type: str = "image/png",
        custom_prompt: Optional[str] = None,
        creative_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze an image for brand compliance.
        
        Args:
            image_data: Image bytes
            image_type: MIME type of the image
            custom_prompt: Optional custom analysis prompt
            creative_type: Optional type hint ("email" or "ad")
            
        Returns:
            Analysis results dictionary
        """
        # Get brand guidelines from vector store
        brand_context = self._get_brand_guidelines()
        
        # Detect creative type if not provided
        if not creative_type:
            creative_type = self._detect_creative_type(image_data)
        
        # Get relevant examples
        examples_context = self._get_examples(creative_type)
        
        # Encode image to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Construct the prompt
        prompt = custom_prompt or self._build_analysis_prompt(brand_context, examples_context, creative_type)
        
        # Call GPT-4o (supports vision)
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{image_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000
        )
        
        analysis_text = response.choices[0].message.content
        
        # Parse the analysis into structured format
        result = {
            "analysis": analysis_text,
            "sources": self._get_relevant_sources(),
            "recommendations": self._extract_recommendations(analysis_text)
        }
        
        return result
    
    def _get_brand_guidelines(self) -> str:
        """
        Retrieve brand guidelines from the vector store.
        
        Returns:
            Formatted brand guidelines text
        """
        guidelines = []
        
        # Get comprehensive color information
        color_results = retrieval_manager.search("brand colors palette hex codes vista blue dusk lawn", top_k=8)
        
        if color_results['documents']:
            guidelines.append("=== BRAND COLORS ===")
            guidelines.append("Nextdoor Brand Color Palette with Hex Codes:")
            guidelines.append("")
            # Collect all unique color information
            seen_colors = set()
            for doc in color_results['documents']:
                if 'hex' in doc.lower() or '#' in doc:
                    # Extract color info
                    lines = doc.split('\n')
                    for line in lines:
                        if any(c in line.lower() for c in ['vista', 'dusk', 'lawn', 'pine', 'dew', 'plaster', 'blue ridge', 'hex', '#']):
                            if line.strip() and line.strip() not in seen_colors:
                                guidelines.append(line.strip())
                                seen_colors.add(line.strip())
        
        # Get typography guidelines
        typo_results = retrieval_manager.search("typography fonts saans helvetica arial", top_k=5)
        
        if typo_results['documents']:
            guidelines.append("")
            guidelines.append("=== TYPOGRAPHY ===")
            for doc in typo_results['documents'][:3]:
                if 'saans' in doc.lower() or 'font' in doc.lower() or 'typeface' in doc.lower():
                    guidelines.append(doc[:500])  # First 500 chars
                    break
        
        # Get logo guidelines  
        logo_results = retrieval_manager.search("logo usage guidelines minimum size clearspace", top_k=3)
        
        if logo_results['documents']:
            guidelines.append("")
            guidelines.append("=== LOGO GUIDELINES ===")
            for doc in logo_results['documents'][:2]:
                if 'logo' in doc.lower() or '19px' in doc or 'minimum' in doc.lower():
                    guidelines.append(doc[:400])
                    break
        
        return "\n".join(guidelines) if guidelines else "No brand guidelines found in the system."
    
    def _detect_creative_type(self, image_data: bytes) -> str:
        """
        Detect if the image is an email, ad, or other type.
        Simple heuristic based on aspect ratio.
        
        Args:
            image_data: Image bytes
            
        Returns:
            "email", "ad", or "other"
        """
        try:
            from PIL import Image
            from io import BytesIO
            
            image = Image.open(BytesIO(image_data))
            width, height = image.size
            aspect_ratio = width / height if height > 0 else 1
            
            # Email templates tend to be tall/narrow
            if aspect_ratio < 0.7:
                return "email"
            # Ads tend to be square or landscape
            elif 0.8 <= aspect_ratio <= 2.0:
                return "ad"
            else:
                return "other"
        except:
            return "other"
    
    def _get_examples(self, creative_type: str) -> str:
        """
        Get approved example designs for the creative type.
        
        Args:
            creative_type: "email", "ad", or "other"
            
        Returns:
            Formatted examples context
        """
        context = ""
        
        # Get creative type specific examples
        if creative_type in ["email", "ad"]:
            examples = retrieval_manager.search_examples(creative_type, top_k=3)
            
            if examples['documents']:
                context += f"\n\n=== APPROVED {creative_type.upper()} EXAMPLES ===\n"
                context += f"Reference these approved Nextdoor {creative_type} designs:\n\n"
                
                for doc, meta in zip(examples['documents'], examples['metadatas']):
                    context += f"Example: {meta.get('name', 'Unnamed')}\n"
                    context += f"From: {meta.get('file_name', 'Unknown file')}\n"
                    context += f"Link: {meta.get('url', '')}\n"
                    # Add snippet of content
                    if len(doc) > 300:
                        context += f"Details: {doc[:300]}...\n\n"
                    else:
                        context += f"Details: {doc}\n\n"
        
        # Always include button/component guidelines from Blocks 3.0 kit
        button_examples = retrieval_manager.search("Blocks 3.0 button component guidelines", top_k=5)
        
        if button_examples['documents']:
            context += f"\n\n=== BUTTON COMPONENT GUIDELINES (Blocks 3.0 Kit) ===\n"
            context += f"Reference these button component standards for any buttons in the design:\n\n"
            
            for doc, meta in zip(button_examples['documents'], button_examples['metadatas']):
                context += f"Component: {meta.get('name', 'Button Component')}\n"
                context += f"From: {meta.get('file_name', 'Blocks 3.0 Kit')}\n"
                if len(doc) > 400:
                    context += f"Guidelines: {doc[:400]}...\n\n"
                else:
                    context += f"Guidelines: {doc}\n\n"
        
        return context
    
    def _build_analysis_prompt(self, brand_context: str, examples_context: str = "", creative_type: str = "other") -> str:
        """
        Build the analysis prompt with brand context.
        
        Args:
            brand_context: Brand guidelines context
            examples_context: Approved example designs
            creative_type: Type of creative being analyzed
            
        Returns:
            Formatted prompt
        """
        creative_type_label = "creative" if creative_type == "other" else creative_type
        
        return f"""You are a brand compliance expert for Nextdoor analyzing {creative_type_label} designs 
against Nextdoor's brand guidelines.

IMPORTANT: You have been provided with:
1. Complete Nextdoor Brand Guidelines with EXACT hex codes
2. Approved example designs to use as reference

Nextdoor Brand Guidelines:
{brand_context}

{examples_context}

INSTRUCTIONS:
- Compare the uploaded image to the approved examples above (if provided)
- Use the EXACT brand colors listed above - compare colors in the image to these specific hex codes
- Reference the approved examples when making recommendations
- Be specific about what matches the approved designs vs. what doesn't

Please analyze the provided {creative_type_label} design and provide a detailed brand compliance report covering:

1. **Color Usage**: 
   - Compare colors in the image to the EXACT brand colors listed above (Vista Blue, Blue Ridge, Dusk, Lawn, Plaster, Dew, Pine)
   - Are the colors aligned with the brand palette? Be specific with hex codes.
   - Identify any colors that deviate from the brand guidelines

2. **Typography**:
   - Check if fonts match Saans (primary) or Helvetica Neue/Arial (fallbacks) as specified above
   - Verify font sizes, weights, and hierarchy
   - Is the typography consistent with brand fonts?

3. **Layout & Spacing**:
   - Does the layout follow design system principles?
   - Is spacing consistent and professional?

4. **Logo Usage**:
   - If a Nextdoor logo is present, check against the guidelines above (minimum 19px, correct clearspace, etc.)
   - Check placement, size, and clear space
   - Verify proper symbol vs. wordmark usage

5. **Button Component Analysis** (if buttons are present):
   - Compare any buttons to the Blocks 3.0 kit guidelines provided above
   - Check button sizing, spacing, corner radius, and padding
   - Verify button colors match the brand palette (Lawn #1B8751, Dusk #232F46, etc.)
   - Ensure button typography follows Saans font guidelines
   - Check button states (hover, active, disabled) if visible

6. **Comparison to Approved Examples** (if examples provided):
   - How does this design compare to the approved examples above?
   - What patterns from the examples are being followed?
   - What patterns from the examples are missing?

7. **Overall Brand Consistency**:
   - Does the creative feel aligned with Nextdoor's brand?
   - What's working well?
   - What looks off-brand?

8. **Recommendations**:
   - What specific improvements should be made?
   - Reference the approved examples when suggesting changes
   - Provide actionable suggestions with exact hex codes and measurements

IMPORTANT: 
- Always reference the EXACT brand colors with hex codes provided above
- Compare to approved examples if provided
- Be specific and actionable in your feedback
"""
    
    def _get_relevant_sources(self) -> list:
        """
        Get relevant brand guideline sources.
        
        Returns:
            List of source citations
        """
        color_sources = retrieval_manager.get_sources("brand colors")[:3]
        typo_sources = retrieval_manager.get_sources("typography fonts")[:2]
        
        return color_sources + typo_sources
    
    def _extract_recommendations(self, analysis_text: str) -> list:
        """
        Extract key recommendations from analysis text.
        
        Args:
            analysis_text: The full analysis text
            
        Returns:
            List of recommendation strings
        """
        # Simple extraction - look for recommendation section
        recommendations = []
        
        if "Recommendations:" in analysis_text or "recommendations:" in analysis_text.lower():
            parts = analysis_text.lower().split("recommendation")
            if len(parts) > 1:
                # Extract bullet points or numbered items after "Recommendations"
                rec_section = parts[-1]
                lines = rec_section.split('\n')
                for line in lines[:5]:  # Take first 5 lines
                    line = line.strip()
                    if line and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                        recommendations.append(line.lstrip('-•0123456789. '))
        
        return recommendations if recommendations else ["See full analysis for recommendations"]
    
    def validate_image(self, image_data: bytes) -> bool:
        """
        Validate that the uploaded data is a valid image.
        
        Args:
            image_data: Image bytes
            
        Returns:
            True if valid image, False otherwise
        """
        try:
            image = Image.open(BytesIO(image_data))
            image.verify()
            return True
        except Exception:
            return False


# Global brand analyzer instance
brand_analyzer = BrandAnalyzer()

