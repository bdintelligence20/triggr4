import React from 'react';
import { Users, Bot, Bell } from 'lucide-react';

interface CompactHubCardProps {
  id: number;
  name: string;
  description: string;
  createdDate: string;
  members: number;
  requests: number;
  image: string;
  onClick: (id: number) => void;
}

const CompactHubCard = ({
  id,
  name,
  description,
  members,
  requests,
  image,
  onClick,
}: CompactHubCardProps) => (
  <div
    onClick={() => onClick(id)}
    className="bg-white rounded-lg shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer overflow-hidden group"
  >
    <div className="relative h-44">
      <img
        src={image}
        alt={name}
        className="w-full h-full object-cover transform transition-transform duration-200 group-hover:scale-105"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
      <div className="absolute bottom-0 left-0 right-0 p-6">
        <div className="flex items-center gap-2 text-white mb-2">
          <Bot size={16} />
          <h3 className="font-medium">{name}</h3>
        </div>
        <p className="text-white/90 text-sm line-clamp-2">{description}</p>
      </div>
    </div>

    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-1.5 text-gray-600">
          <Users size={16} />
          <span>{members} members</span>
        </div>
        <div className="flex items-center gap-1.5 text-emerald-400">
          <Bell size={16} />
          <span>{requests}</span>
        </div>
      </div>
    </div>
  </div>
);

export default CompactHubCard;