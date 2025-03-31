import React, { useState, useEffect } from 'react';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import { ChevronDown, Check } from 'lucide-react';

// Define the country code interface
interface CountryCode {
  code: string;
  name: string;
  dial_code: string;
  flag: string;
}

// List of common country codes
const countryCodes: CountryCode[] = [
  { code: 'ZA', name: 'South Africa', dial_code: '+27', flag: '🇿🇦' },
  { code: 'US', name: 'United States', dial_code: '+1', flag: '🇺🇸' },
  { code: 'GB', name: 'United Kingdom', dial_code: '+44', flag: '🇬🇧' },
  { code: 'AU', name: 'Australia', dial_code: '+61', flag: '🇦🇺' },
  { code: 'CA', name: 'Canada', dial_code: '+1', flag: '🇨🇦' },
  { code: 'DE', name: 'Germany', dial_code: '+49', flag: '🇩🇪' },
  { code: 'FR', name: 'France', dial_code: '+33', flag: '🇫🇷' },
  { code: 'IN', name: 'India', dial_code: '+91', flag: '🇮🇳' },
  { code: 'NG', name: 'Nigeria', dial_code: '+234', flag: '🇳🇬' },
  { code: 'KE', name: 'Kenya', dial_code: '+254', flag: '🇰🇪' },
  { code: 'GH', name: 'Ghana', dial_code: '+233', flag: '🇬🇭' },
  { code: 'ZW', name: 'Zimbabwe', dial_code: '+263', flag: '🇿🇼' },
  { code: 'NA', name: 'Namibia', dial_code: '+264', flag: '🇳🇦' },
  { code: 'BW', name: 'Botswana', dial_code: '+267', flag: '🇧🇼' },
  { code: 'MZ', name: 'Mozambique', dial_code: '+258', flag: '🇲🇿' },
];

interface CountryCodeSelectorProps {
  selectedCountryCode: string;
  onSelect: (countryCode: string) => void;
  className?: string;
}

const CountryCodeSelector: React.FC<CountryCodeSelectorProps> = ({
  selectedCountryCode,
  onSelect,
  className = '',
}) => {
  const [open, setOpen] = useState(false);
  const [selectedCountry, setSelectedCountry] = useState<CountryCode | null>(null);

  // Find the selected country based on the dial code
  useEffect(() => {
    const country = countryCodes.find(c => c.dial_code === selectedCountryCode);
    setSelectedCountry(country || null);
  }, [selectedCountryCode]);

  const handleSelect = (country: CountryCode) => {
    setSelectedCountry(country);
    onSelect(country.dial_code);
    setOpen(false);
  };

  return (
    <DropdownMenu.Root open={open} onOpenChange={setOpen}>
      <DropdownMenu.Trigger asChild>
        <button
          className={`flex items-center gap-1 px-2 py-2 border rounded-l-lg focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 ${className}`}
          aria-label="Select country code"
        >
          <span className="text-lg">{selectedCountry?.flag || '🌍'}</span>
          <span className="text-sm font-medium">{selectedCountry?.dial_code || '+00'}</span>
          <ChevronDown size={16} className="text-gray-500" />
        </button>
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className="bg-white rounded-lg shadow-lg p-1 w-64 max-h-80 overflow-y-auto z-50"
          sideOffset={5}
        >
          <DropdownMenu.Label className="px-2 py-1.5 text-xs font-medium text-gray-500">
            Select Country Code
          </DropdownMenu.Label>
          
          <DropdownMenu.Separator className="h-px bg-gray-200 my-1" />
          
          {countryCodes.map((country) => (
            <DropdownMenu.Item
              key={country.code}
              className="flex items-center gap-2 px-2 py-2 text-sm rounded-md cursor-pointer outline-none hover:bg-gray-100 focus:bg-gray-100"
              onSelect={() => handleSelect(country)}
            >
              <span className="text-lg">{country.flag}</span>
              <span className="flex-1">{country.name}</span>
              <span className="text-gray-500">{country.dial_code}</span>
              {selectedCountry?.code === country.code && (
                <Check size={16} className="text-emerald-500" />
              )}
            </DropdownMenu.Item>
          ))}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
};

export default CountryCodeSelector;
