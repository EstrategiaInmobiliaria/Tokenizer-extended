import { useState } from "react";
import type { LeadQualification } from "~/types/palm-diamante";

interface LeadFormProps {
  onSubmit?: (lead: LeadQualification) => void;
}

export function LeadQualificationForm({ onSubmit }: LeadFormProps) {
  const [formData, setFormData] = useState<LeadQualification>({
    tieneLiquidezFirma: false,
    puedePagarMensualidad: false,
    quiereCreditoHipotecario: "no",
    nombre: "",
    email: "",
    telefono: "",
    notas: "",
  });

  const [showContactForm, setShowContactForm] = useState(false);

  const isQualified =
    formData.tieneLiquidezFirma &&
    formData.puedePagarMensualidad &&
    formData.quiereCreditoHipotecario !== "no";

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSubmit) {
      onSubmit(formData);
    }
    // Aquí conectarías con tu CRM/EasyBroker
    alert(
      isQualified
        ? "✅ Lead calificado! Te contactaremos por WhatsApp."
        : "📧 Gracias. Te enviaremos información a tu email para nurturing."
    );
  };

  return (
    <div className="flex flex-col gap-6 rounded-lg border-2 border-slate-200 bg-white p-6 shadow-lg">
      <div className="flex flex-col gap-2">
        <h2 className="text-2xl font-bold text-slate-900">
          Formulario de Calificación
        </h2>
        <p className="text-sm text-slate-600">
          3 preguntas para filtrar inversionistas verificados
        </p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-6">
        {/* Pregunta 1: Liquidez para firma */}
        <div className="flex flex-col gap-3 rounded-md border border-slate-200 bg-slate-50 p-4">
          <label className="text-sm font-semibold text-slate-900">
            1. ¿Cuentas con $353k - $868k para firma de contrato en los próximos 15 días?
          </label>
          <p className="text-xs text-slate-600">
            Según el modelo que elijas (B1 Entry a Penthouse)
          </p>
          <div className="flex gap-4">
            <label className="flex cursor-pointer items-center gap-2">
              <input
                type="radio"
                name="liquidez"
                checked={formData.tieneLiquidezFirma === true}
                onChange={() =>
                  setFormData({ ...formData, tieneLiquidezFirma: true })
                }
                className="h-4 w-4 border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-slate-700">Sí</span>
            </label>
            <label className="flex cursor-pointer items-center gap-2">
              <input
                type="radio"
                name="liquidez"
                checked={formData.tieneLiquidezFirma === false}
                onChange={() =>
                  setFormData({ ...formData, tieneLiquidezFirma: false })
                }
                className="h-4 w-4 border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-slate-700">No</span>
            </label>
          </div>
          {!formData.tieneLiquidezFirma && (
            <div className="rounded-md bg-amber-50 border border-amber-200 p-3 text-xs text-amber-800">
              ⚠️ Sin liquidez inmediata, tu lead irá a nurturing por email, no a WhatsApp directo.
            </div>
          )}
        </div>

        {/* Pregunta 2: Mensualidad sostenible */}
        <div className="flex flex-col gap-3 rounded-md border border-slate-200 bg-slate-50 p-4">
          <label className="text-sm font-semibold text-slate-900">
            2. ¿Puedes sostener $16k - $39k mensuales por 42 meses?
          </label>
          <p className="text-xs text-slate-600">
            Dependiendo del modelo y la torre (21, 26 o 42 meses)
          </p>
          <div className="flex gap-4">
            <label className="flex cursor-pointer items-center gap-2">
              <input
                type="radio"
                name="mensualidad"
                checked={formData.puedePagarMensualidad === true}
                onChange={() =>
                  setFormData({ ...formData, puedePagarMensualidad: true })
                }
                className="h-4 w-4 border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-slate-700">Sí</span>
            </label>
            <label className="flex cursor-pointer items-center gap-2">
              <input
                type="radio"
                name="mensualidad"
                checked={formData.puedePagarMensualidad === false}
                onChange={() =>
                  setFormData({ ...formData, puedePagarMensualidad: false })
                }
                className="h-4 w-4 border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-slate-700">
                No / Necesito ver números
              </span>
            </label>
          </div>
        </div>

        {/* Pregunta 3: Crédito hipotecario */}
        <div className="flex flex-col gap-3 rounded-md border border-slate-200 bg-slate-50 p-4">
          <label className="text-sm font-semibold text-slate-900">
            3. ¿Quieres que te pre-aprobemos tu crédito hipotecario del 80% desde ahora con BBVA/Banorte?
          </label>
          <p className="text-xs text-slate-600">
            Gestionamos la pre-aprobación antes de la entrega
          </p>
          <div className="flex flex-col gap-2">
            <label className="flex cursor-pointer items-center gap-2">
              <input
                type="radio"
                name="credito"
                checked={formData.quiereCreditoHipotecario === "si_rfc"}
                onChange={() =>
                  setFormData({ ...formData, quiereCreditoHipotecario: "si_rfc" })
                }
                className="h-4 w-4 border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-slate-700">
                Sí, tengo RFC (empresa o actividad empresarial)
              </span>
            </label>
            <label className="flex cursor-pointer items-center gap-2">
              <input
                type="radio"
                name="credito"
                checked={formData.quiereCreditoHipotecario === "si_persona_fisica"}
                onChange={() =>
                  setFormData({
                    ...formData,
                    quiereCreditoHipotecario: "si_persona_fisica",
                  })
                }
                className="h-4 w-4 border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-slate-700">
                Sí, como persona física
              </span>
            </label>
            <label className="flex cursor-pointer items-center gap-2">
              <input
                type="radio"
                name="credito"
                checked={formData.quiereCreditoHipotecario === "no"}
                onChange={() =>
                  setFormData({ ...formData, quiereCreditoHipotecario: "no" })
                }
                className="h-4 w-4 border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-slate-700">No</span>
            </label>
          </div>
        </div>

        {/* Status de calificación */}
        <div
          className={`rounded-md border-2 p-4 ${
            isQualified
              ? "border-green-500 bg-green-50"
              : "border-amber-500 bg-amber-50"
          }`}
        >
          <h3 className="mb-2 text-sm font-bold">
            {isQualified ? "✅ Lead Calificado" : "⚠️ Lead para Nurturing"}
          </h3>
          <p className="text-xs">
            {isQualified
              ? "Este perfil va directo a WhatsApp con Jaime Wilk + Diana Ondarza para corrida financiera."
              : "Este perfil necesita contenido educativo por email antes de contacto directo."}
          </p>
        </div>

        {/* Formulario de contacto */}
        {isQualified && !showContactForm && (
          <button
            type="button"
            onClick={() => setShowContactForm(true)}
            className="rounded-md bg-blue-600 px-6 py-3 font-semibold text-white shadow-md transition-colors hover:bg-blue-700"
          >
            Continuar con mis datos
          </button>
        )}

        {showContactForm && (
          <div className="flex flex-col gap-4 rounded-md border border-slate-200 bg-white p-4">
            <h3 className="text-sm font-bold text-slate-900">
              Información de Contacto
            </h3>

            <input
              type="text"
              placeholder="Nombre completo *"
              required
              value={formData.nombre}
              onChange={(e) =>
                setFormData({ ...formData, nombre: e.target.value })
              }
              className="rounded-md border border-slate-300 px-4 py-2 text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <input
              type="email"
              placeholder="Email *"
              required
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
              className="rounded-md border border-slate-300 px-4 py-2 text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <input
              type="tel"
              placeholder="WhatsApp *"
              required
              value={formData.telefono}
              onChange={(e) =>
                setFormData({ ...formData, telefono: e.target.value })
              }
              className="rounded-md border border-slate-300 px-4 py-2 text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <textarea
              placeholder="Notas adicionales (opcional)"
              value={formData.notas}
              onChange={(e) =>
                setFormData({ ...formData, notas: e.target.value })
              }
              rows={3}
              className="rounded-md border border-slate-300 px-4 py-2 text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <button
              type="submit"
              className="rounded-md bg-green-600 px-6 py-3 font-bold text-white shadow-md transition-colors hover:bg-green-700"
            >
              🚀 Enviar y recibir corrida financiera
            </button>
          </div>
        )}
      </form>
    </div>
  );
}
