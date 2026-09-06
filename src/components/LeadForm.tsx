import { useState } from 'react';
import type { LeadInput } from '~/models/lead-scoring';
import { Input } from './Input';
import { Select } from './Select';
import { Button } from './Button';

interface LeadFormProps {
  onSubmit: (lead: LeadInput) => void;
  onCancel?: () => void;
}

export const LeadForm = ({ onSubmit, onCancel }: LeadFormProps) => {
  const [formData, setFormData] = useState<Partial<LeadInput>>({
    name: '',
    email: '',
    phone: '',
    source: 'organic',
    propertyInterest: {
      priceRange: {
        min: 0,
        max: 0,
      },
      propertyType: 'apartment',
      purpose: 'investment',
      timeline: '1-3_months',
      financingStatus: 'unsure',
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.name && formData.email && formData.propertyInterest) {
      onSubmit(formData as LeadInput);
    }
  };

  const updatePropertyInterest = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      propertyInterest: {
        ...prev.propertyInterest!,
        [field]: value,
      },
    }));
  };

  const updatePriceRange = (field: 'min' | 'max', value: string) => {
    const numValue = parseFloat(value) || 0;
    setFormData(prev => ({
      ...prev,
      propertyInterest: {
        ...prev.propertyInterest!,
        priceRange: {
          ...prev.propertyInterest!.priceRange,
          [field]: numValue,
        },
      },
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 rounded-lg bg-white p-6 shadow-lg">
      <h2 className="text-2xl font-bold">📋 Nuevo Lead</h2>

      <div className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-semibold">Nombre Completo *</label>
          <Input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
            placeholder="Juan Pérez"
            required
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-semibold">Email *</label>
          <Input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
            placeholder="juan@example.com"
            required
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-semibold">Teléfono</label>
          <Input
            type="tel"
            value={formData.phone}
            onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
            placeholder="+52 55 1234 5678"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-semibold">Edad</label>
          <Input
            type="number"
            value={formData.age || ''}
            onChange={(e) => setFormData(prev => ({ ...prev, age: parseInt(e.target.value) || undefined }))}
            placeholder="35"
            min="18"
            max="100"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-semibold">Ubicación</label>
          <Input
            type="text"
            value={formData.location}
            onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
            placeholder="Ciudad de México, CDMX"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-semibold">Fuente del Lead *</label>
          <select
            value={formData.source}
            onChange={(e) => setFormData(prev => ({ ...prev, source: e.target.value as any }))}
            className="w-full rounded border border-gray-300 px-3 py-2"
            required
          >
            <option value="organic">Orgánico (Google, SEO)</option>
            <option value="paid_ads">Publicidad Pagada</option>
            <option value="referral">Referido</option>
            <option value="social_media">Redes Sociales</option>
            <option value="email">Email Marketing</option>
            <option value="other">Otro</option>
          </select>
        </div>
      </div>

      <div className="border-t pt-4">
        <h3 className="mb-3 text-lg font-bold">🏠 Interés en Propiedad</h3>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm font-semibold">Precio Mínimo ($) *</label>
              <Input
                type="number"
                value={formData.propertyInterest?.priceRange.min || ''}
                onChange={(e) => updatePriceRange('min', e.target.value)}
                placeholder="1000000"
                required
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-semibold">Precio Máximo ($) *</label>
              <Input
                type="number"
                value={formData.propertyInterest?.priceRange.max || ''}
                onChange={(e) => updatePriceRange('max', e.target.value)}
                placeholder="5000000"
                required
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-semibold">Tipo de Propiedad *</label>
            <select
              value={formData.propertyInterest?.propertyType}
              onChange={(e) => updatePropertyInterest('propertyType', e.target.value)}
              className="w-full rounded border border-gray-300 px-3 py-2"
              required
            >
              <option value="apartment">Departamento</option>
              <option value="house">Casa</option>
              <option value="condo">Condominio</option>
              <option value="land">Terreno</option>
              <option value="commercial">Comercial</option>
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-semibold">Propósito de Compra *</label>
            <select
              value={formData.propertyInterest?.purpose}
              onChange={(e) => updatePropertyInterest('purpose', e.target.value)}
              className="w-full rounded border border-gray-300 px-3 py-2"
              required
            >
              <option value="investment">Inversión</option>
              <option value="primary_residence">Residencia Principal</option>
              <option value="vacation_home">Casa de Vacaciones</option>
              <option value="unsure">No estoy seguro</option>
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-semibold">Timeline de Compra *</label>
            <select
              value={formData.propertyInterest?.timeline}
              onChange={(e) => updatePropertyInterest('timeline', e.target.value)}
              className="w-full rounded border border-gray-300 px-3 py-2"
              required
            >
              <option value="immediate">Inmediato (esta semana)</option>
              <option value="1-3_months">1-3 meses</option>
              <option value="3-6_months">3-6 meses</option>
              <option value="6-12_months">6-12 meses</option>
              <option value="over_1_year">Más de 1 año</option>
              <option value="just_browsing">Solo estoy viendo opciones</option>
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-semibold">Estado de Financiamiento *</label>
            <select
              value={formData.propertyInterest?.financingStatus}
              onChange={(e) => updatePropertyInterest('financingStatus', e.target.value)}
              className="w-full rounded border border-gray-300 px-3 py-2"
              required
            >
              <option value="cash_buyer">Comprador en efectivo</option>
              <option value="pre_approved">Pre-aprobado para crédito</option>
              <option value="needs_financing">Necesito financiamiento</option>
              <option value="unsure">No estoy seguro</option>
            </select>
          </div>
        </div>
      </div>

      <div>
        <label className="mb-1 block text-sm font-semibold">Notas adicionales</label>
        <textarea
          value={formData.notes || ''}
          onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
          placeholder="Información adicional sobre el lead..."
          className="w-full rounded border border-gray-300 px-3 py-2"
          rows={3}
        />
      </div>

      <div className="flex gap-3">
        <Button type="submit" className="flex-1">
          🎯 Calificar Lead
        </Button>
        {onCancel && (
          <Button type="button" onClick={onCancel} className="bg-gray-500 hover:bg-gray-600">
            Cancelar
          </Button>
        )}
      </div>
    </form>
  );
};
