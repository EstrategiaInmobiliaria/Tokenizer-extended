"""
Database Models - SQLAlchemy ORM
Modelos para persistencia de análisis y proyectos
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Project(Base):
    """Modelo de Proyecto de Inversión"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    project_type = Column(String(50), nullable=False)  # 'real_estate', 'industrial', etc.
    status = Column(String(50), default="draft")  # draft, active, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    wacc_analyses = relationship("WACCAnalysis", back_populates="project", cascade="all, delete-orphan")
    dcf_analyses = relationship("DCFAnalysis", back_populates="project", cascade="all, delete-orphan")
    optimizations = relationship("OptimizationAnalysis", back_populates="project", cascade="all, delete-orphan")


class WACCAnalysis(Base):
    """Análisis de WACC guardado"""
    __tablename__ = "wacc_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Parámetros de entrada
    risk_free_rate = Column(Float, nullable=False)
    market_return = Column(Float, nullable=False)
    corporate_tax_rate = Column(Float, nullable=False)
    equity_value = Column(Float, nullable=False)
    debt_value = Column(Float, nullable=False)
    beta = Column(Float, nullable=False)
    debt_rate = Column(Float, nullable=False)
    
    # Resultados
    wacc = Column(Float, nullable=False)
    cost_of_equity = Column(Float, nullable=False)
    cost_of_debt_after_tax = Column(Float, nullable=False)
    detailed_results = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    project = relationship("Project", back_populates="wacc_analyses")


class DCFAnalysis(Base):
    """Análisis DCF guardado"""
    __tablename__ = "dcf_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Parámetros
    initial_investment = Column(Float, nullable=False)
    discount_rate = Column(Float, nullable=False)
    projection_years = Column(Integer, nullable=False)
    
    # Flujos de caja (almacenados como JSON)
    cash_flows = Column(JSON, nullable=False)
    
    # Resultados
    npv = Column(Float, nullable=False)
    irr = Column(Float, nullable=False)
    profitability_index = Column(Float, nullable=False)
    payback_period = Column(Float, nullable=False)
    accept_project = Column(Boolean, nullable=False)
    
    # Análisis completo
    full_analysis = Column(JSON)
    scenarios = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    project = relationship("Project", back_populates="dcf_analyses")


class OptimizationAnalysis(Base):
    """Análisis de optimización guardado"""
    __tablename__ = "optimization_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Configuración
    products_config = Column(JSON, nullable=False)
    constraints_config = Column(JSON, nullable=False)
    fixed_costs = Column(Float, default=0)
    
    # Resultados
    success = Column(Boolean, nullable=False)
    method = Column(String(100))
    optimal_quantities = Column(JSON)
    optimal_profit = Column(Float)
    detailed_results = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    project = relationship("Project", back_populates="optimizations")
