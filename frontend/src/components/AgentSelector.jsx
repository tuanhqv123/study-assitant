import React, { useState, useEffect } from "react";
import { Check, ChevronDown } from "lucide-react";

const AgentSelector = ({ selectedAgent, onAgentChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [agents, setAgents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Simplified agent display names without prefixes
  const displayNameMap = {
    gemma: "Gemma 3 4B",
    qwen: "Qwen3 30B A3B",
    llama: "Llama 4 Maverick",
    deepseek: "DeepSeek V3 0324",
    mistral: "Mistral (Default)",
  };

  // Fetch available agents from the backend
  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const response = await fetch("http://localhost:8000/agents");
        if (!response.ok) {
          throw new Error(`Failed to fetch agents: ${response.status}`);
        }
        const data = await response.json();
        setAgents(data.agents || []);
        setIsLoading(false);
      } catch (error) {
        console.error("Error fetching agents:", error);
        // Fallback to some default agents if server is unavailable
        setAgents([
          {
            id: "mistral",
            display_name: "Mistral (Default)",
            is_default: true,
          },
        ]);
        setIsLoading(false);
      }
    };

    fetchAgents();
  }, []);

  // Get the currently selected agent
  const currentAgent = selectedAgent
    ? agents.find((a) => a.id === selectedAgent) ||
      agents.find((a) => a.is_default)
    : agents.find((a) => a.is_default);

  const getDisplayName = (agent) => {
    return displayNameMap[agent.id] || agent.display_name;
  };

  return (
    <div className="relative h-10 w-full">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex h-full w-full items-center justify-between px-3 py-1 rounded-md border border-border bg-card hover:bg-accent/50 transition-colors text-sm"
        disabled={isLoading}
      >
        {isLoading ? (
          <span className="text-sm">Loading...</span>
        ) : (
          <>
            <span className="truncate block">
              {getDisplayName(currentAgent)}
            </span>
            <ChevronDown className="w-3 h-3 flex-shrink-0 ml-1" />
          </>
        )}
      </button>

      {isOpen && !isLoading && (
        <div className="absolute top-full left-0 mt-1 z-50 w-56 rounded-md shadow-lg bg-card border border-border">
          <div className="p-1 max-h-80 overflow-y-auto">
            {agents.map((agent) => (
              <button
                key={agent.id}
                className={`w-full text-left px-3 py-2 text-sm rounded-md flex items-center justify-between ${
                  selectedAgent === agent.id ? "bg-accent" : "hover:bg-muted"
                }`}
                onClick={() => {
                  onAgentChange(agent.id);
                  setIsOpen(false);
                }}
              >
                <div className="flex items-center truncate">
                  <span className="truncate">{getDisplayName(agent)}</span>
                </div>
                {selectedAgent === agent.id && (
                  <Check className="w-4 h-4 flex-shrink-0" />
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentSelector;
