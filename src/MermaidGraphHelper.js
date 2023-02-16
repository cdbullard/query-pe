import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

function MermaidGraph({ graphDefinition }) {
  const graphRef = useRef(null);

  useEffect(() => {
    // Re-render graph on initialization or graph definition change
    mermaid.render('graph', graphDefinition, (svg) => {
      if (graphRef.current) {
        graphRef.current.innerHTML = svg;
        // Remove the 'data-processed' attribute to force re-render
        graphRef.current.removeAttribute('data-processed');
      }
    });
  }, [graphDefinition]);

  return (
    <div ref={graphRef} className="mermaid">
      {graphDefinition}
    </div>
  );
}

export default MermaidGraph;
