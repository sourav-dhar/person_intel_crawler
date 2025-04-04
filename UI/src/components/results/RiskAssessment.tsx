import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { SearchResult } from '../../types/search';

interface RiskAssessmentProps {
  result: SearchResult;
}

const RiskAssessment = ({ result }: RiskAssessmentProps) => {
  const gaugeRef = useRef<SVGSVGElement | null>(null);
  
  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'low':
        return '#10B981'; // green-500
      case 'medium':
        return '#F59E0B'; // amber-500
      case 'high':
        return '#EF4444'; // red-500
      case 'critical':
        return '#7F1D1D'; // red-900
      default:
        return '#6B7280'; // gray-500
    }
  };
  
  useEffect(() => {
    if (!gaugeRef.current) return;
    
    // Clear previous visualization
    d3.select(gaugeRef.current).selectAll('*').remove();
    
    // Set up dimensions
    const width = 300;
    const height = 200;
    const margin = { top: 20, right: 30, bottom: 30, left: 30 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;
    
    // Create SVG
    const svg = d3.select(gaugeRef.current)
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Define gauge arc
    const radius = Math.min(chartWidth, chartHeight) / 2;
    const arc = d3.arc()
      .innerRadius(radius * 0.7)
      .outerRadius(radius)
      .startAngle(-Math.PI / 2)
      .endAngle(Math.PI / 2);
    
    // Create gauge background
    const gaugeGroup = svg.append('g')
      .attr('transform', `translate(${chartWidth / 2},${chartHeight / 2})`);
    
    // Risk segments
    const segments = [
      { risk: 'low', color: '#10B981', start: -Math.PI / 2, end: -Math.PI / 6 },
      { risk: 'medium', color: '#F59E0B', start: -Math.PI / 6, end: Math.PI / 6 },
      { risk: 'high', color: '#EF4444', start: Math.PI / 6, end: Math.PI / 2 }
    ];
    
    // Add segments
    segments.forEach((segment) => {
      const segmentArc = d3.arc()
        .innerRadius(radius * 0.7)
        .outerRadius(radius)
        .startAngle(segment.start)
        .endAngle(segment.end);
        
      gaugeGroup.append('path')
        .attr('d', segmentArc as any)
        .attr('fill', segment.color)
        .attr('stroke', '#fff')
        .attr('stroke-width', 1);
        
      // Add risk label
      const labelAngle = (segment.start + segment.end) / 2;
      const labelRadius = radius * 1.15;
      gaugeGroup.append('text')
        .attr('x', Math.cos(labelAngle) * labelRadius)
        .attr('y', Math.sin(labelAngle) * labelRadius)
        .attr('text-anchor', 'middle')
        .attr('alignment-baseline', 'middle')
        .attr('font-size', '12px')
        .attr('fill', segment.color)
        .text(segment.risk.toUpperCase());
    });
    
    // Add needle
    const confidenceScore = result.confidence_score;
    const riskLevel = result.risk_level.toLowerCase();
    let needleValue;
    
    // Map risk level to a value between -1 (low) and 1 (high)
    switch (riskLevel) {
      case 'low':
        needleValue = -0.67 + (confidenceScore * 0.33); // Range between -0.67 and -0.33
        break;
      case 'medium':
        needleValue = -0.33 + (confidenceScore * 0.67); // Range between -0.33 and 0.33
        break;
      case 'high':
        needleValue = 0.33 + (confidenceScore * 0.33); // Range between 0.33 and 0.67
        break;
      case 'critical':
        needleValue = 0.67 + (confidenceScore * 0.33); // Range between 0.67 and 1.0
        break;
      default:
        needleValue = 0;
    }
    
    // Convert to angle (from -90° to 90°)
    const needleAngle = needleValue * Math.PI / 2;
    
    // Draw needle
    gaugeGroup.append('line')
      .attr('x1', 0)
      .attr('y1', 0)
      .attr('x2', Math.cos(needleAngle) * radius * 0.8)
      .attr('y2', Math.sin(needleAngle) * radius * 0.8)
      .attr('stroke', '#1F2937')
      .attr('stroke-width', 3)
      .attr('stroke-linecap', 'round');
      
    // Add needle circle
    gaugeGroup.append('circle')
      .attr('cx', 0)
      .attr('cy', 0)
      .attr('r', radius * 0.08)
      .attr('fill', '#1F2937');
      
    // Add current risk text
    gaugeGroup.append('text')
      .attr('x', 0)
      .attr('y', radius * 0.4)
      .attr('text-anchor', 'middle')
      .attr('font-size', '22px')
      .attr('font-weight', 'bold')
      .attr('fill', getRiskColor(riskLevel))
      .text(riskLevel.toUpperCase());
      
    // Add confidence text
    gaugeGroup.append('text')
      .attr('x', 0)
      .attr('y', radius * 0.55)
      .attr('text-anchor', 'middle')
      .attr('font-size', '12px')
      .attr('fill', '#6B7280')
      .text(`Confidence: ${Math.round(result.confidence_score * 100)}%`);
  }, [result]);
  
  return (
    <div className="p-4">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Risk Assessment</h3>
      
      <div className="flex flex-col items-center justify-center">
        <svg ref={gaugeRef} className="w-full max-w-xs"></svg>
        
        <div className="mt-6 w-full max-w-md">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="bg-green-100 p-3 rounded-lg">
              <span className="block font-medium text-green-700">Low</span>
              <span className="text-xs text-green-800">Minimal concerns</span>
            </div>
            <div className="bg-amber-100 p-3 rounded-lg">
              <span className="block font-medium text-amber-700">Medium</span>
              <span className="text-xs text-amber-800">Some concerns</span>
            </div>
            <div className="bg-red-100 p-3 rounded-lg">
              <span className="block font-medium text-red-700">High/Critical</span>
              <span className="text-xs text-red-800">Significant concerns</span>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">Risk Justification</h4>
            <p className="text-sm text-gray-600 whitespace-pre-line">
              {result.risk_justification || "No detailed risk justification available."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskAssessment;