interface Props { title: string }

export default function PlaceholderPage({ title }: Props) {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">{title}</h1>
      <div className="bg-white rounded-xl border border-gray-200 p-6 mt-4">
        <p className="text-sm text-gray-400 text-center py-8">
          Módulo en desarrollo — próxima fase.
        </p>
      </div>
    </div>
  );
}